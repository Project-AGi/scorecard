# AGi Scorecard

Model benchmark results for the Grace project. Each section identifies its
scorer and protocol; custom harness checks and partial historical runs are
labeled separately from official benchmark scores.

## Regenerating

```bash
cd benchmarks
python3 scorecard_all.py                 # one table to stdout
python3 scorecard_all.py --markdown      # the tables in this file
```

`scorecard_all.py` reads the raw result files from each suite and normalizes
them to a 0-100 scale so benchmarks with different units can be read side by
side. Per-benchmark raw data and the exact protocol live in each suite's
`README.md`.

## Model candidates

### Front-end chat models

| Label | Model / build | Size | Intended role | Status | Justification |
|---|---|---:|---|---|---|
| `ministral3-8b-nymphaea-rp-iq4xs` | Ministral 3 8B Nymphaea RP i1-IQ4_XS (run label: `nymphaea-rp`) | 8B | RP/creative Ministral variant (same speed as IQ4_XS) | 🔵 Top contender  | Better MBPP+ than the Abliterated build; RP-specific chat evaluation still matters. |
| `ministral3-8b-abliterated-iq4xs` | Ministral 3 8B Instruct 2512 Abliterated i1-IQ4_XS (run label: `ministral-iq4xs`; local `/opt/agi/models/ministral3-8b/`) | 8B | Daily-driver router model: fastest, lowest VRAM | 🟡 Under consideration | Active default; fastest prefill, 5.9 GiB VRAM, no IFEval truncations. |
| `minicpm5-2b` | MiniCPM 5 | 2B | Cheap helper or robot-side model | N/A  | Reference for model comparison on interactive and agentic scorings. |
| `agents-a1-4b` | Agents A1 | 4B | Cheap helper or robot-side model | N/A | Reference for model comparison on interactive and agentic scorings. |
| `neohorse-1-4b` | NeoHorse | 4B | Cheap helper or robot-side model | N/A | Reference for model comparison on interactive and agentic scorings. |
| `ministral3-14b` | Ministral 3 14B Instruct 2512 UD-Q4KXL | 14B | Front-end chatbot for conversation and persona | 🔴 Rejected | Not enough VRAM to load if running together with an agentic model. |

### Back-end agentic models

| Label | Model / build | Size | Intended role | Status | Justification |
|---|---|---:|---|---|---|
| `occamy-i1` | Occamy 1.0 i1-Q4_K_M + mmproj F16 (RustingStrata 1.3.1, ctx 16384) | 30B MoE | Daily-driver MoE agent | 🟡 Under consideration | Canvas results vary from 0 to 7/10; all tested variants hit the output-token cap. |
| `occamy-apex` | Occamy 1.0 APEX I-Quality + mmproj F16 (RustingStrata 1.3.1, ctx 16384) | 30B MoE | Best-quality MoE agent | 🔵 Top contender | Canvas leader at 10/10 twice; truncates at the output-token cap in all tested variants. |
| `bonsai-2.5` | Ternary Bonsai 2.5 27B Q2_0-MTP + mmproj BF16 (llama.cpp b12766, `--reasoning-budget 512`) | 27B | Reasoning agent (most consistent renderer) | 🟡 Under consideration | Never truncates; Canvas scores are lower than Occamy APEX, and long-context TTFT is 14.5s at 8K. |
| `ornith-1.5-35b-a3b-heretic` | **Ornith-1.5-35B-A3B-Heretic-MTP-APEX-GSQ-RCO-IQ3_S.gguf** + `mmproj-Ornith-1.5-35B-A3B-Heretic-MTP-BF16.gguf` (RustingStrata 1.4.2, ctx 16384) | 35B-A3B | Fast uncensored MoE agent | 🔵 Top contender | Fastest uncensored agentic model tested: 114.4 tok/s decode @8K with MTP+ngram (IQ3_S, calibrated). Quality/canvas/IFEval not yet benchmarked. |
| `swift1.5-qwen3.8-27B` | Swift 1.5 Qwen 3.8 27B GSQ-RCO IQ3_S MTP | 27B | Back-end agent for reasoning, tool calling, and vision | 🟡 Under consideration | Candidate for vision routing; comparable end-to-end Grace evaluation is pending. |

Legend: 🟢 Selected · 🔵 Top contender · 🟡 Under consideration · 🔴 Rejected

In this planned split, visual inputs can be routed to `swift1.5-qwen3.8-27B`, so Ministral vision
is not needed unless the front-end must process images directly. Scores for the
two component models do not predict the routed Grace system; evaluate that
system end to end when it is available.

Inference perf (temp 0, 256 output tokens, 2 reps; VRAM/RAM are sampled peaks;
14B entries excluded):

| Build | Prompt tokens | Prefill tok/s | Decode tok/s | TTFT | VRAM | RAM PSS |
|---|---:|---:|---:|---:|---:|---:|
| ministral3-8b-abliterated-iq4xs (active default, llama.cpp) | 512 / 2048 / 8192 | 2264 / 2982 / 3124 | 54.4 / 49.4 / 38.1 | 487 ms / 921 ms / 2946 ms | 5.9 GiB | 1.1 / 1.4 / 2.0 GiB |
| ministral3-8b-abliterated-iq4nl (deleted quant, kept for record) | 512 / 2048 / 8192 | 2123 / 2864 / 2985 | 52.4 / 49.9 / 37.3 | 516 ms / 945 ms / 3093 ms | 6.0 GiB | 1.1 / 1.4 / 2.0 GiB |
| ministral3-8b-abliterated-q4km (deleted quant, kept for record) | 512 / 2048 / 8192 | 1952 / 2616 / 2761 | 49.6 / 45.9 / 35.0 | 557 ms / 1040 ms / 3319 ms | 6.4 GiB | 1.2 / 1.4 / 2.1 GiB |
| ministral3-8b-abliterated-udq4kxl (deleted quant, kept for record) | 512 / 2048 / 8192 | 562 / 1007 / 3255 | 49.3 / 46.0 / 35.2 | 1276 ms / 1491 ms / 2185 ms | 6.4 GiB | 1.2 / 1.4 / 2.1 GiB |
| ministral3-8b-nymphaea-rp-iq4xs | 512 / 2048 / 8192 | (identical to IQ4_XS) | 56.3 / 37.9 | 2.9s @8K | 5.9 GiB | (identical) |

Scores (8B only; 14B excluded):

| Benchmark | Build | n | Result |
|---|---|---:|---|
| IFEval strict / loose | ministral3-8b-nymphaea-rp-iq4xs | 541 | **66.7 / 68.4** (17 trunc) |
| IFEval strict / loose | ministral3-8b-abliterated-q4km (Modal) | 541 | 56.6 / 64.1 (2 trunc) |
| IFEval strict / loose | ministral3-8b-abliterated-iq4xs (Modal) | 541 | 56.2 / 66.4 (1 trunc) |
| IFEval strict / loose | ministral3-8b-abliterated-iq4xs (local, active) | 541 | 55.8 / 63.8 (0 trunc) |
| IFEval strict / loose | ministral3-8b-abliterated-iq3s (Modal) | 541 | 49.9 / 56.4 (39 trunc) |
| IFBench single-turn (prompt loose / strict) | ministral3-8b-abliterated-iq4xs (Modal) | 300 | 26.3 / 20.0 (10 token-limited) |
| EvalPlus pass@1 (HumanEval base/+ / MBPP base/+) | ministral3-8b-abliterated-iq4xs (Modal) | 164 / 378 | 0.835 / 0.787 / 0.743 / 0.624 |
| EvalPlus pass@1 (HumanEval base/+ / MBPP base/+) | ministral3-8b-nymphaea-rp-iq4xs (local) | 164 / 378 | 0.811 / 0.768 / 0.798 / 0.687 |
| Grace Chatbot Elo (blind pairwise) | ministral3-14b (source run label: `ministral`) | 6 scripts / 21 turns | **1539** (most likeable in sample) |

**Other model scores (non-8B):**

| Benchmark | Build | n | Result |
|---|---|---:|---|
| EvalPlus pass@1 (HumanEval base/+ / MBPP base/+) | swift15-qwen3.8-27b-local (Modal, UD-IQ3_S) | 164 / 378 | 0.598 / 0.591 / 0.690 / 0.627 |

### Small models (2–4B) — inference perf (llama.cpp b12826, temp 0, 256 output tokens, 3 reps)

Temp 0, 256 output tokens, 3 reps; ctx 16384; single GPU for the 4B models.
Full JSON in `results/inference_perf/<label>/summary.json`.

| Model | Build | Prompt tokens | Prefill tok/s | Decode tok/s | TTFT | VRAM | RAM PSS |
|---|---|---:|---:|---:|---:|---:|---:|
| minicpm5-2b | MiniCPM5-2B Q8_0 (2.5 GB) | 512 / 2048 / 8192 | 6,247 / 9,028 / 8,183 | 111.1 / 106.6 / 96.6 | 102.7 / 269.7 / 1,147.1 ms | 3.5 GB | 1.0 / 1.3 / 2.5 GB |
| neohorse-1-4b | NeoHorse 4B Q4_K_M (2.6 GB) | 512 / 2048 / 8192 | 2,264 / 3,685 / 4,713 | 88.4 / 87.2 / 82.1 | 262.9 / 607.4 / 1,935.1 ms | 3.9 GB | 1.9 / 2.7 / 4.2 GB |
| agents-a1-4b | Agents A1 4B Q4_K_M (2.6 GB) | 512 / 2048 / 8192 | 2,325 / 3,493 / 4,660 | 88.8 / 88.2 / 82.9 | 361.9 / 710.2 / 1,947.0 ms | 3.9 GB | 2.0 / 3.1 / 4.8 GB |
| agents-a1-4b + mmproj | Agents A1 4B Q4_K_M + mmproj (3.2 GB) | 512 / 2048 / 8192 | 2,337 / 3,503 / 4,594 | 88.8 / 88.4 / 81.2 | 359.4 / 707.6 / 1,968.7 ms | 4.8 GB | 2.1 / 3.2 / 4.9 GB |
| inkling-2-mini-uncensored | Inkling-2-Mini-Uncensored AD-Q4_K + mmproj BF16 (16 GB, RustingStrata 1.4.2, ngram-simple, vrm128) | 512 / 2048 / 8192 | 234 / 276 / 238 | 42.7 / 36.1 / 37.3 | 2,332.6 / 7,551.1 / 34,616.9 ms | 10.8 / 10.8 / 10.8 GB | 15.6 / 15.7 / 15.8 GB |

minicpm5-2b is ~2.7× faster to decode and prefill than the 4B models and uses the least VRAM/RAM despite Q8_0. neohorse and agents-a1 are within ~3% of each other. Adding the Agents A1 mmproj costs ~0.9 GB VRAM with no measurable speed change (text throughput unaffected). Inkling-2-Mini uncensored is much heavier (16 GB, RustingStrata) with slower prefill/decode but larger context-capable architecture.

### Agentic models — inference perf (RustingStrata 1.4.2, ctx 16384, temp 0, 256 output, 2 reps)

**Calibrated settings (RustingStrata, ctx 16384, thinking-budget 2048):**
- **Ornith IQ3_S**: `MTP+ngram, vrm512, chunk4096, mtp1, short32` — `strata-Ornith-1.5-35B-A3B-Heretic-MTP-APEX-GSQ-RCO-IQ3_S.json`
- **Occamy i1 Q4_K_M**: `ngram, vrm256, chunk2048, mtp0, short32` — `strata-occamy-1.0-abliterated-safetensors.i1-Q4_K_M.json`
- **Occamy apex Q6_K**: `ngram, vrm512, chunk2048, mtp0, short32` — `strata-occamy-1.0-abliterated-APEX-I-QUALITY-Q6_K.json`
- **JoyFox Q6_K**: `MTP+ngram, vrm512, chunk4096, mtp2, short32` — `strata-JoyFox-Qwen3.6-35B-A3B-RP-Aggressive.i1-Q6_K.json`
- **Gemma 4 26B A4B StyleTune V2 Q6_K**: `ngram, chunk512, mtp0, short32` (local sweep anomalous/regressed; prior 111.5 tok/s@8K kept as reference) — `strata-Gemma-4-26B-A4B-StyleTune-V2.i1-Q6_K.json`
- **Inkling-2-Mini-Uncensored-AD-Q4_K**: `ngram-simple, vrm128, chunk256, mtp0, short32` — `strata-Inkling-2-Mini-Uncensored-AD-Q4_K.json`

| Model | Quant | Speculation | Decode@512/2K/8K | Prefill@512/2K/8K | TTFT@512/2K/8K | VRAM |
|---|---|---|---:|---:|---:|---:|
| **Ornith-1.5-35B-A3B-Heretic-MTP-APEX-GSQ-RCO-IQ3_S** + mmproj BF16 | IQ3_S | MTP+ngram | 118.7/118.7/114.4 | 667/1541/1880 | 791ms/1.34s/4.38s | ~11.0GB |
| Occamy 1.0 i1 abliterated | Q4_K_M | ngram, vrm256 (no MTP head) | 112.3/104.5/103.5 | 533/1074/1336 | 999ms/1.93s/6.15s | ~11.0GB |
| Occamy 1.0 apex abliterated | Q6_K | ngram, vrm512 (no MTP head) | 110.3/77.3/95.0 | 373/987/1239 | 1.40s/2.09s/6.64s | ~11.0GB |
| JoyFox Qwen3.6 RP Aggressive | Q6_K | MTP+ngram (mtp2) | 66.4/71.3/82.6 | 166/621/1198 | 4.23s/3.37s/6.87s | ~11.0GB |
| Gemma 4 26B A4B StyleTune V2 | Q6_K | ngram only (MTP drafter mismatched) | 116.8/116.6/111.5 | 1084/1530/1766 | 497ms/2.73s/7.68s | — |
| Gemma 4 26B A4B StyleTune V2 | Q6_K | MTP+ngram (mismatched drafter) | 22.8/18.7/13.6 | 71/100/88 | 7.36s/20.54s/93.50s | ~10.4GB |
| Bonsai 2.5 27B | Q2_0 ternary | none (llama.cpp b12766) | 32.4/31.8/30.2 | 514/569/578 | 1.09s/3.76s/14.50s | ~10.6GB (2 GPUs) |
| Inkling-2-Mini | Q4_K | ngram (no MTP head) | 23.9/21.1/21.3 | 122/136/130 | 4.48s/15.29s/63.15s | ~5.9GB |

Notes: Occamy has no MTP head; Ornith MTP gives +28% over ngram-only. Gemma MTP drafter (unsloth base) mismatches StyleTune V2 and tanks speed; without MTP Gemma is fast. Inkling has no MTP head. JoyFox native MTP gives minimal gain over ngram-only.

### Combined — 3-model comparison (canvas 40 / decode 25 / TTFT@8K 20 / memory 15)

Source: `results/combined-3models.json` (best rendered structural + perf).

| Model | Best canvas | Mean | Usable ≥5 | Composite |
|---|---:|---:|---:|---:|
| Occamy 1.0 APEX | 10.00 (loose-multi) | 5.00 | 2/4 | **86.5** |
| Occamy 1.0 i1 | 7.00 (loose-single) | 4.06 | 2/4 | **80.9** |
| Bonsai 2.5 27B | 8.25 (strict-multi) | 6.62 | 4/4 | **61.5** |

APEX wins on peak quality, Bonsai on consistency (never blank, never
truncated, 4/4 usable), i1 on speed. No single model dominates all axes.

## Benchmarks and protocol

| Benchmark | What it measures | n | Protocol | Official scorer |
|---|---|---:|---|---|
| [BFCL V4](benchmarks/bfcl/README.md) | Full function calling and agentic tool use: single-turn, multi-turn, live, memory/search, hallucination, and format sensitivity | category-specific | Pinned official V4 harness; complete protocol required for overall score | yes (official BFCL evaluator) |
| [EQ-Bench v2 (historical)](benchmarks/eqbench/README.md) | Emotion recognition — rating 4 emotions per scenario | 171 | temp 0.01, max_tokens 60, up to 3 parse attempts | yes (official full-scale) |
| [EQ-Bench v4 / Creative Writing v3](benchmarks/eqbench/README.md) | Applied emotional/social intelligence / judged writing quality | 120 personas / 32 prompts × 3 | Pinned official protocols and judges; v4 uses 16-message conversations; writing temp 0.7, min_p 0.1 | yes (official; runs pending) |
| [EvalPlus](benchmarks/evalplus/README.md) | Code-generation correctness on HumanEval+ and MBPP+ with expanded tests | dataset-specific | Greedy generation; official sandbox/scorer; pin package and image for each run | yes (official EvalPlus scorer) |
| [Grace Canvas Eval](benchmarks/grace_canvas_eval/README.md) | `canvas_draw` tool-call validity and drawing quality | 8 tasks / T1 matrix | Production DRAW_INSTRUCTIONS, temp 0.0, max_tokens 6144 | scene-graph checks + deterministic structural scorer (T1); VLM judge secondary-only |
| [Grace Chatbot Eval](benchmarks/grace_chatbot_eval/README.md) | Persona fit: warmth, coherence, persona, overall | 6 scripts / 21 turns | SOUL.md + timestamp, temp 0.7, blind pairwise rating | human rater; Elo K=32 |
| [IFEval](benchmarks/ifeval/README.md) | Verifiable instruction/format compliance on final responses | 541 | temp 0.0, max_tokens 14336, raw prompt, no system prompt | yes (Google Research scorer, vendored) |
| [IFBench single-turn](benchmarks/ifbench/README.md) | Precise instruction following | 300 | Pinned test data, temp 0, one response, prompt-level loose accuracy primary | yes (pinned official library) |
| [IFBench multi-turn](benchmarks/ifbench/README.md) | Constraint isolation in released fixed conversation history | 1,387 | Pinned `ifbench_constraints/test`, temp 0, generate final response only | yes (pinned official library) |
| [LiveCodeBench](benchmarks/livecodebench/README.md) | Code generation with execution-based pass@k | 1,055 | Pinned cumulative release_v6 lite, n=10, temp 0.2, top_p 0.95 | yes (pinned official checker and estimator) |
| [LongMemEval](benchmarks/longmemeval/README.md) | Recall, multi-session reasoning, knowledge updates, temporal reasoning, and abstention | 500 | Full-history long-context baseline; official QA evaluator uses a configured LLM judge | yes (official evaluator; no result recorded) |

BFCL V4, EQ-Bench v4, Creative Writing v3, LiveCodeBench,
and LongMemEval have no completed model scores here. IFBench single-turn now
has a Ministral run (official scorer); the multi-turn runner still needs a
model endpoint. EvalPlus now has
HumanEval+/MBPP+ for `ministral3-8b-abliterated-iq4xs` and
`ministral3-8b-nymphaea-rp-iq4xs` (official scorer).
EQ-Bench v2 results and the incomplete BFCL V3 artifacts below are historical;
the incomplete BFCL V3 artifacts below are historical; the V3 subset rates are
not full benchmark scores. Synthetic scorer fixtures and smoke tests are not
benchmark results. INTIMA and AICompanionBench are research-readiness entries,
not runnable integrations ([guide](benchmarks/companion_safety/README.md)).

**Thinking mode.** EQ-Bench results remain think-off. Official IFEval does
not prescribe a thinking mode; the current Scorecard protocol uses each
endpoint's normal default (Swift/Qwen on, Ministral with no separate thinking
mode). `--think-off` is a separately recorded IFEval variant, and scores from
different modes should not be compared as one protocol. IFEval scores below
were collected under the previous think-off protocol. Canvas is reported per
arm because the arms disagree by more than any other benchmark here.

---

## Results

### IFEval — instruction following (strict / loose)

| Model | n | Strict | Loose | Time |
|---|---:|---:|---:|---:|
| gemma-4-26b-styletune-v2-rs (Modal) | 541 | **88.2** | **89.8** | 172 min |
| minicpm5-2b | 541 | 85.6 | 87.2 | 82 min |
| swift | 541 | 82.1 | 86.9 | API, rate-limited |
| neohorse-1-4b | 541 | 79.1 | 83.0 | 113 min |
| agents-a1-4b | 541 | 76.3 | 81.2 | 117 min |
| ministral3-14b | 541 | 65.1 | 71.5 | 219 min |

`ministral3-8b-abliterated-iq4xs` is the active router default: fastest prefill, 6.0 GB VRAM, zero
truncations, within ~1pp of Q4_K_M. Nymphaea-RP is kept as the second
Ministral variant for RP/creative work.

| IFEval score box — recommended daily driver | Strict | Loose | Truncated |
|---|---:|---:|---:|
| ministral3-8b-abliterated-iq4xs (local) | **55.8%** | **63.8%** | **0 / 541** |

### IFBench single-turn — precise instruction following (official scorer)

Pinned data (`IFBench_test.jsonl`, rev 48891866), temp 0, max_tokens 4096,
n=1, primary metric prompt-level loose accuracy.

| Model | n | Prompt loose | Prompt strict | Token-limited | Timeouts |
|---|---:|---:|---:|---:|---:|
| ministral3-8b-abliterated-iq4xs (Modal) | 300 | 26.3 | 20.0 | 10 | 0 |

Instruction-level: strict 23.3, loose 29.7. First IFBench datapoint — no
baseline to rank against yet; the multi-turn suite (1,387 constraints) still
needs a configured endpoint.

### EvalPlus — code generation (pass@1 base / plus, official scorer)

Greedy single-sample generation against the local OpenAI-compatible endpoint,
evaluated with the official EvalPlus scorer (pinned `ganler/evalplus` image;
package 0.3.1). File values recomputed per-task from `*_eval_results.json`.

| Model | HumanEval (164) base | HumanEval+ | MBPP (378) base | MBPP+ |
|---|---:|---:|---:|---:|
| ministral3-8b-abliterated-iq4xs (Modal) | **0.835** | **0.787** | 0.743 | 0.624¹ |
| ministral3-8b-nymphaea-rp-iq4xs (local) | 0.811 | 0.768 | **0.798** | **0.687**² |

¹ Official scorer stdout said 0.624; the saved file recomputes to 0.630.
² Official scorer stdout said 0.687; the saved file recomputes to 0.689
(resume created duplicate samples for 265/378 tasks after a mid-run kill;
the unbiased estimator handles this).

Nymphaea trades ~2pp on HumanEval for +5.5pp/+6.3pp on MBPP — the RP
finetune did not cost code ability overall.

### Grace Canvas Eval — lighthouse matrix (T1, structural /10)

`GRACE_CONSOLE_DIR=/home/oppa-ai/AGi/console`, temp 0.0, max_tokens 6144,
vision passes on. `structural` is the deterministic scene-graph score
(tower 1.5 / lantern 2.5 / setting 1.5 / dusk 1.0 / glow 1.5 / coherence 2.0;
lantern requires a lit lamp, glow requires tower-axis proximity). The VLM
judge is unreliable at this resolution (gave the best render 0/10) and is
kept as an optional secondary signal only. `check` is the legacy
presence-only score — a blank scene can score 5/5, so read `structural`.

| Run | Check | Valid | Render | Trunc | Steps | Wall | Structural |
|---|---:|---:|---:|---:|---:|---:|---:|
| occamy-apex/loose-multi | 1.0 | 1 | Y | 1 | 20 | 217s | **10.00** |
| occamy-apex/strict-single | 0.8 | 1 | Y | 1 | 16 | 130s | **10.00** |
| bonsai/strict-multi | 1.0 | 1 | Y³ | 0 | 38 | 150s | **8.25** |
| occamy-i1/loose-single | 1.0 | 1 | Y | 1 | 10 | 95s | 7.00 |
| bonsai/strict-single | 1.0 | 1 | Y³ | 0 | 16 | 61s | 6.25 |
| bonsai/loose-multi | 1.0 | 1 | Y | 0 | 39 | 159s | 6.00 |
| bonsai/loose-single | 0.8 | 1 | Y | 0 | 15 | 62s | 6.00 |
| occamy-i1/strict-multi | 0.8 | 1 | Y | 1 | 15 | 229s | 5.00 |
| occamy-i1/loose-multi | 0.6 | 1 | Y | 1 | 82 | 303s | 4.25 |
| occamy-apex/loose-single | 0.6 | 1 | Y | 1 | 18 | 159s | 0.00 |
| occamy-apex/strict-multi | 0.8 | 0 | Y | 1 | 2 | 427s | 0.00 |
| occamy-i1/strict-single | 1.0 | 1 | Y | 1 | 4 | 137s | 0.00 |

³ Re-rendered post-hoc from saved actions with the `dedupe_ids` harness fix;
model output untouched. Bonsai never truncates; both Occamy quants burn the
full 6144-token budget (`finish=length`) on 4/4 variants.

### Inference Perf — speed / VRAM / RAM (temp 0, 256 output tokens, 2 reps)

Full groups in `results/inference_perf/<label>/summary.json`. TTFT = time to
first token; VRAM is shared-GPU peak, PSS is host RAM peak.

**Occamy 1.0 i1-Q4_K_M** (`occamy-i1-perf2`, RustingStrata 1.3.1, ctx 16384):

| Prompt tokens | Prefill tok/s | Decode tok/s | TTFT | VRAM | RAM PSS |
|---:|---:|---:|---:|---:|---:|
| 512 | 477 | 118.6 | 1096 ms | 10.9 GiB | 19.1 GiB |
| 2048 | 1057 | 90.4 | 1959 ms | 11.0 GiB | 20.3 GiB |
| 8192 | 1713 | 85.1 | 4813 ms | 11.0 GiB | 21.0 GiB |

**Occamy 1.0 APEX I-Quality** (`occamy-apex-perf`, RustingStrata 1.3.1, ctx 16384):

| Prompt tokens | Prefill tok/s | Decode tok/s | TTFT | VRAM | RAM PSS |
|---:|---:|---:|---:|---:|---:|
| 512 | 388 | 102.5 | 1353 ms | 10.9 GiB | 19.8 GiB |
| 2048 | 904 | 85.1 | 2304 ms | 10.9 GiB | 21.3 GiB |
| 8192 | 1473 | 78.2 | 5585 ms | 11.0 GiB | 22.0 GiB |

**Bonsai 2.5 27B Q2_0-MTP** (`bonsai-perf`, llama.cpp b12766):

| Prompt tokens | Prefill tok/s | Decode tok/s | TTFT | VRAM | RAM PSS |
|---:|---:|---:|---:|---:|---:|
| 512 | 514 | 32.4 | 1091 ms | 10.4 GiB | 2.3 GiB |
| 2048 | 569 | 31.8 | 3759 ms | 10.4 GiB | 3.9 GiB |
| 8192 | 578 | 30.2 | 14498 ms | 10.4 GiB | 6.4 GiB |

Also on file: `ministral-nymphaea-perf` (IQ4_XS-class: 56.3/37.9 decode,
2.9s TTFT@8K, 5.9 GiB VRAM — identical to IQ4_XS), `ministral-q4km-perf`,
`ministral-udq4xl-perf`, `ministral-iq4nl-perf` (deleted quants, kept for the
record: all slower than IQ4_XS for no quality win). Bonsai's long-context
TTFT (14.5s @8K) is its main weakness; Occamy pays ~21 GB host RAM for its
expert cache at ctx 16384; RustingStrata VRAM is ~constant (~11 GB) across
quants.

### Ministral 3 (8B) — grouped summary (inference perf first, then scores)

### Historical BFCL V3 responses — incomplete samples

The V3 runner has been removed. These retained response files cover different
fractions of the old 1,240-task local run and are **not official full BFCL
scores**. They are kept temporarily until a complete V4 evaluation is run.

| Model | Correct responses | Coverage | Accuracy on saved subset |
|---|---:|---:|---:|
| minicpm5-2b | 826/1,071 | 86% | 77.1% |
| neohorse-1-4b | 602/745 | 60% | 80.8% |
| ministral3-14b | 664/852 | 69% | 77.9% |
| agents-a1-4b | 278/423 | 34% | 65.7% |

Coverage and category mix differ, so these subset rates should not be ranked
against one another or compared with BFCL V4 leaderboard scores.

### EQ-Bench v2 — emotion recognition

| Model | n | Score | Parseable |
|---|---:|---:|---:|
| neohorse-1-4b | 171 | **57.0** | 171/171 |
| agents-a1-4b | 171 | 56.7 | 171/171 |
| swift1.5-qwen3.8-27B | 171 | 56.8 | 171/171 |
| ministral3-14b | 171 | 54.8 | 171/171 |
| minicpm5-2b | 171 | 40.4 | 171/171 |

### Grace Canvas Eval — `canvas_draw` tool calling

**Historical pipeline results:** the corrected protocol forwards reasoning effort
and preserves the draft during review. Existing review deltas and effort-labelled
runs need rerunning; the table below has not been recomputed. See the
[corrected pipeline notes](benchmarks/grace_canvas_eval/README.md#corrected-pipeline-protocol-version-2).

Eight tasks scored from the canvas engine's own scene graph — no reference
images, no judge. `check_score` is the fraction of per-task checks passed
(object count, palette, layout rhythm, coverage, overlap, edit semantics);
`valid_rate` is the fraction of calls the validator accepted without repair.

| Run | Arm | Drew | Actions | check_score | valid_rate |
|---|---|---:|---:|---:|---:|
| swift1.5-qwen3.8-27B | think-off | 8/8 | 3691 | **0.690** | 0.500 |
| swift1.5-qwen3.8-27B | think-off, forced tool | 8/8 | 6662 | **0.690** | 0.375 |
| neohorse-1-4b | think-off | 8/8 | 73 | 0.595 | 0.750 |
| ministral3-14b | think-off | 8/8 | 36 | 0.595 | 0.375 |
| minicpm5-2b | think-on, budget-capped | 8/8 | 49 | 0.595 | 0.250 |
| agents-a1-4b | think-on, budget-capped | 8/8 | 27 | 0.595 | 0.375 |
| neohorse-1-4b | think-on, budget-capped | 8/8 | 45 | 0.571 | 0.625 |
| swift1.5-qwen3.8-27B | think-on | 5/8 | 1404 | 0.500 | 0.125 |
| agents-a1-4b | think-off | 8/8 | 18 | 0.405 | **1.000** |
| minicpm5-2b | think-off | 8/8 | 22 | 0.310 | 0.375 |

Scores are post-repair (see *Blank renders* below): the engine now drops
poison actions instead of voiding the scene, and tier-4 renders seed+edit.
`Drew` counts tasks with at least one emitted action; `render_rate` is 1.0
across the board after the fix, so it is omitted.

#### Blank renders — root causes, all fixed or explained

Every blank-white PNG traced to one of four causes; none required rerunning
the model:

1. **Unbounded thinking starved the tool call** — the trace consumed all
   3072 tokens, 0 actions emitted. Fixed by `--reasoning-budget 1024` on the
   serving config (think-on arms rerun under the cap).
2. **One poison action voided the scene** — e.g. the `swift1.5-qwen3.8-27B` lighthouse action 11
   (`x: [58, 175]`, a list where a number belongs). The old repair only
   handled three slip types; anything else failed revalidation and the
   harness fell back to an empty list. Fixed in the engine:
   `repair_model_actions` is now per-action (drop the poison, keep the
   fourteen good ones), plus coercions for list-valued coords and
   point-less lines. Valid input passes through byte-identical (self-tested).
3. **Tier-4 rendered without the seed** — the harness rendered only the edit
   actions. Fixed (seed+edit), T4 rescored to 4/4 for every model.
4. **Genuine model failures** — T5's 3205-action dump (over the 100-action
   cap) and empty think-on emissions remain blank, correctly.

### Grace Chatbot Eval — blind persona preference (Elo)

| Model | Votes | Elo | Win rate | Per-dimension wins |
|---|---:|---:|---:|---|
| ministral3-14b (source label: `ministral`) | 16 | **1539** | 31% | coherence 3/3, overall 5/5, persona 3/3, warmth 5/5 |
| swift1.5-qwen3.8-27B | 11 | 1461 | 18% | coherence 3/3, overall 2/2, persona 4/4, warmth 2/2 |

Small n — single rater, six scripts. Treat as a directional signal only.

---

## What the numbers say

**Ministral 3 14B is the most likeable model in the small blind persona sample, while
its 8B variants show mixed instruction-following results.** It wins the blind
persona test (Elo 1539); on IFEval, Nymphaea RP leads the tested Ministral
8B variants, while IQ4_XS remains the active low-VRAM router default.
Ministral 3 14B scored 65.1 strict / 71.5 loose on IFEval. For Grace this is
the central tension: SOUL's
emoji-and-colon prefix and 1–2 sentence limit are hard
constraints, and "warmest" does not mean "follows the contract".

**The smaller models show different profiles across tests.** `minicpm5-2b`
tops the completed IFEval results (85.6) but has the lowest historical EQ-Bench
v2 score (40.4). These separate model-only scores do not validate a model-role
split or the planned Ministral-front-end/`swift1.5-qwen3.8-27B`-back-end system. The smaller
models have not been evaluated as helpers in that routed system.

**Standard function calling still needs a full run.** BFCL V4 is the active
tool-calling evaluation and has not yet been run. Grace Canvas Eval is a
separate custom test: the current `swift1.5-qwen3.8-27B` think-off runs have the highest
recorded `check_score` (0.690), while prompts, reasoning modes, and action
counts vary across runs. These canvas results do not measure the combined
Ministral/`swift1.5-qwen3.8-27B` system.

**`valid_rate` and `check_score` measure different things.** A call can be
well-formed without producing a complete scene, and a strong scene score can
include repaired actions. Read both metrics together; neither alone measures
the quality of the routed agent system.

**Forcing the tool did not improve the `swift1.5-qwen3.8-27B` canvas score in this run.** The
think-off forced and unforced runs both scored 0.690, while the forced run
used 6,662 actions versus 3,691. It increased output without improving the
scene-graph score.

**APEX has the highest ceiling, Bonsai the highest floor.** On the lighthouse
matrix APEX produced the only 10/10 renders but also two blanks; Bonsai never
blanked or truncated and is usable on all four variants (6.0–8.25). Occamy i1
sits between on quality while leading on speed (118.6 tok/s decode).

**Nymphaea beats the default Ministral at MBPP, loses slightly at HumanEval.**
The RP finetune is not a code downgrade: +5.5pp/+6.3pp on MBPP against −2pp
on HumanEval, at identical speed and VRAM.

**Canvas `check_score` alone misleads; `structural` is the quality signal.**
A blank sky+rock scene scored check 5/5, and the old VLM judge gave a messy
saucer-top 9/10. The deterministic scene-graph scorer (validated: reproduces
the old judge exactly where it was right on 7 Swift renders) now ranks
Apex 10 > Bonsai 8.25/6.25 > i1 7 > blanks 0, matching eyeball judgment.

---

## In flight

| Run | State |
|---|---|
| IFBench multi-turn ministral3-8b-abliterated-iq4xs (1,387) | generating vs local router :8080, ~13s/task (~5h), resumable; log `/tmp/opencode/ifbench-multiturn.log` |
| Last completions | ministral3-8b-nymphaea-rp-iq4xs EvalPlus (HumanEval+ 0.768, MBPP+ 0.687), Occamy/Bonsai lighthouse matrix + rescore, `inference_perf` for all three, IFBench single-turn ministral3-8b-abliterated-iq4xs 26.3 |

## Gaps

1. **BFCL V4 run pending** — the active test is the official full V4
   protocol. Its memory and web-search tasks use benchmark tools/backends; they
   do not directly measure AIVA's SQLite history or its `/web` path. The
   retained V3 responses above are incomplete historical samples.
2. **Coverage differs by suite** — all five listed models have historical
   EQ-Bench v2 results; the blind persona preference results cover only
   `swift1.5-qwen3.8-27B` and `ministral3-14b`.
3. **Multi-turn scores pending** — IFBench single-turn is recorded above;
   the fixed-history multi-turn runner (1,387 constraints) is integrated and a
   full ministral3-8b-abliterated-iq4xs run is underway against the local router (resumable output dir
   `benchmarks/ifbench/results/multiturn-ministral-iq4xs`). Score it with
   `--stage score` on completion and record prompt loose/strict here.
4. **No persistent-memory retrieval measurement** — LongMemEval full-history
   is a useful baseline, but Grace needs a retrieval adapter to evaluate her
   PostgreSQL-backed memory with the same questions.
5. **Embeddings untested** — `voyage-4-nano` needs a retrieval benchmark, not
   a chat benchmark.
6. **Canvas has no image-level judge** — `check_score` verifies countable
   properties (object count, palette, rhythm, coverage), not whether the
   drawing resembles the subject. A deterministic structural scorer now covers
   the T1-lighthouse task (tower/lantern/setting/dusk/glow/coherence, 0–10);
   the optional VLM judge (`--judge-base-url`/`--judge-model`) proved
   unreliable at 336–600px vision resolution and stays secondary-only.
7. **Code-generation coverage is thin** — EvalPlus has HumanEval+/MBPP+ for
   the two Ministral 8B builds only; Occamy, Bonsai, and the small models
   have no code scores yet.


