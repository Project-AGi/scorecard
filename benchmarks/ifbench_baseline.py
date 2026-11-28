"""IFBench protocols; scoring is delegated to the official evaluation library."""
import copy
import dataclasses
import importlib
import json
import sys
import zipfile

from baseline_common import HERE, checkout, download, initialize, parser, read_jsonl, responses, write_json

REVISION = "488918665d53f867fa908a293769ec6e71e74aec"
MULTITURN_REVISION = "e1ea65c5178fbeac522a26d12b8c71a298e9846d"
NLTK_REVISION = "550b6625bcef1f2abff2ff770a5a0d272c9c6b2a"


def configure_limits(args):
    """Choose fixed budgets before generation, independent of test outcomes."""
    ministral = "ministral" in (args.model or "").lower()
    if args.max_tokens is None:
        args.max_tokens = 4096 if ministral else 8192
    if args.request_timeout is None:
        args.request_timeout = 600 if ministral else 1200
    if args.request_timeout <= 0:
        raise ValueError("request-timeout must be positive")


def prepare_nltk():
    """Supply immutable resources before upstream's automatic downloader runs."""
    import nltk
    root = HERE / ".cache" / f"nltk-{NLTK_REVISION}"
    for resource in ("tokenizers/punkt", "tokenizers/punkt_tab", "corpora/stopwords",
                     "taggers/averaged_perceptron_tagger_eng"):
        archive = download(f"https://raw.githubusercontent.com/nltk/nltk_data/{NLTK_REVISION}/packages/{resource}.zip",
                           root / (resource + ".zip"))
        if not (root / resource).exists():
            with zipfile.ZipFile(archive) as z:
                z.extractall((root / resource).parent)
    nltk.data.path.insert(0, str(root))


def run(multiturn=None):
    cli = parser("IFBench single-turn and released fixed-history multi-turn")
    cli.set_defaults(max_tokens=None, request_timeout=None)
    cli.add_argument("--suite", choices=["single", "multiturn"], default="single")
    args = cli.parse_args()
    configure_limits(args)
    if multiturn is None:
        multiturn = args.suite == "multiturn"
    if args.n != 1 or args.temperature != 0:
        raise ValueError("IFBench baseline requires n=1 and temperature=0")
    official = checkout("https://github.com/allenai/IFBench.git", REVISION,
                        args.official or HERE / ".cache" / "IFBench")
    protocol = {"suite": "IFBench multi-turn" if multiturn else "IFBench single-turn",
                "official_revision": REVISION, "temperature": 0, "top_p": 1,
                "nltk_data_revision": NLTK_REVISION,
                "history": "released messages including fixed assistant turn" if multiturn else "single user prompt",
                "primary_metric": "prompt_loose",
                "generation_policy": "bounded-v1",
                "request_timeout_seconds": args.request_timeout,
                "token_limit_policy": "score returned final text; continue",
                "timeout_policy": "score empty response; continue; report separately",
                "answer_extraction": "message.content only; reasoning_content saved separately"}
    if getattr(args, "think_off", False):
        protocol["thinking"] = "disabled via chat_template_kwargs.enable_thinking=false"
    if getattr(args, "reasoning_effort", None):
        protocol["reasoning_effort"] = args.reasoning_effort
    reasoning_budget = int(getattr(args, "reasoning_budget", 0) or 0)
    if reasoning_budget > 0:
        protocol["reasoning_budget"] = reasoning_budget
    if multiturn:
        path = download(f"https://huggingface.co/datasets/allenai/IFBench_multi-turn/resolve/{MULTITURN_REVISION}/ifbench_constraints/test-00000-of-00001.parquet",
                        HERE / ".cache" / f"ifbench-multiturn-{MULTITURN_REVISION}.parquet")
        import pyarrow.parquet as pq
        rows = pq.read_table(path).to_pylist()
        protocol.update(dataset="allenai/IFBench_multi-turn", dataset_revision=MULTITURN_REVISION,
                        config="ifbench_constraints", split="test")
    else:
        path = official / "data" / "IFBench_test.jsonl"
        rows = read_jsonl(path)
        protocol.update(dataset="data/IFBench_test.jsonl", dataset_revision=REVISION)
    total = len(rows)
    rows = rows[:args.limit] if args.limit else rows
    if not rows or len({str(r['key']) for r in rows}) != len(rows):
        raise ValueError("Empty dataset or duplicate keys")
    for row in rows:
        if not row["prompt"] or not row["instruction_id_list"] or len(row["instruction_id_list"]) != len(row["kwargs"]):
            raise ValueError("Unexpected IFBench instruction schema")
        if multiturn and [m["role"] for m in row["messages"]] != ["user", "assistant", "user"]:
            raise ValueError("Unexpected released multi-turn schema")
    tasks = [{"id": r["key"], "row": r} for r in rows]
    initialize(args, protocol, path, total)
    if args.stage == "prepare":
        print(f"Prepared {len(rows)}/{total} tasks: {protocol['suite']}")
        return

    def messages(task):
        row = task["row"]
        if not multiturn:
            return [{"role": "user", "content": row["prompt"]}]
        turns = row["messages"]
        if [m["role"] for m in turns] != ["user", "assistant", "user"]:
            raise ValueError("Unexpected released multi-turn schema")
        return turns

    outputs = responses(args, tasks, messages, bounded=True)
    if outputs is None:
        return
    prepare_nltk()
    sys.path.insert(0, str(official))
    evaluator = importlib.import_module("evaluation_lib")
    # Ensure the registry also comes from the verified checkout, not another install.
    registry = importlib.import_module("ifbench")
    if not str(registry.__file__).startswith(str(official) + "/"):
        raise ValueError("IFBench registry was imported from outside the pinned checkout")
    result = {"suite": protocol["suite"], "model": args.model, "n": len(rows),
              "full_run": len(rows) == total, "protocol": protocol,
              "max_tokens": args.max_tokens, "request_timeout_seconds": args.request_timeout}
    records = read_jsonl(args.output / "responses.jsonl")
    result["generation"] = {
        "token_limited": sum(r["finish_reason"] == "length" for r in records),
        "timed_out": sum(r["finish_reason"] == "timeout" for r in records),
        "empty_answers": sum(not r["response"].strip() for r in records),
    }
    for mode in ("strict", "loose"):
        graded = []
        for row, output in zip(rows, outputs):
            inp = evaluator.InputExample(**{k: copy.deepcopy(row[k]) for k in ("key", "instruction_id_list", "prompt", "kwargs")})
            inp.kwargs = [{k: v for k, v in kw.items() if v is not None} for kw in inp.kwargs]
            grade = getattr(evaluator, "test_instruction_following_" + mode)(inp, {inp.prompt: output[0]})
            graded.append(dataclasses.asdict(grade))
        write_json(args.output / f"official_{mode}.json", graded)
        result[f"prompt_{mode}"] = sum(g["follow_all_instructions"] for g in graded) / len(graded)
        flags = [flag for g in graded for flag in g["follow_instruction_list"]]
        result[f"instruction_{mode}"] = sum(flags) / len(flags)
    write_json(args.output / "summary.json", result)
    print(json.dumps(result, indent=2))
