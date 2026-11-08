<div align="center">

<h1>KitAgent</h1>

<p><strong>Run your AI agent from the browser or terminal</strong></p>

<p>An open-source AI agent runtime and visual workbench</p>
<p><sub>Conversational tasks · Live tool tracking · Human approval · Session memory · Kubernetes sandboxes</sub></p>

<p>
  <a href="https://github.com/zed123214/kitagent/actions/workflows/ci.yml"><img src="https://github.com/zed123214/kitagent/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12" /></a>
  <a href="frontend/package.json"><img src="https://img.shields.io/badge/React-19-149ECA?logo=react&logoColor=white" alt="React 19" /></a>
  <a href="docs/kubernetes-sandbox.md"><img src="https://img.shields.io/badge/Kubernetes-Sandbox-326CE5?logo=kubernetes&logoColor=white" alt="Kubernetes Sandbox" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-F5C542" alt="MIT License" /></a>
</p>

[中文](README.md) · **English**

[Demo](#demo) · [Operator Workflow](#operator-demo) · [Features](#features) · [Architecture](#architecture) · [Quick Start](#quick-start) · [Documentation](#docs)

</div>

---

KitAgent is for developers who build and use AI automation tools. Describe a task in your browser or terminal, let the agent read your project, run commands, and edit files, then continue in the same conversation. Use the workbench to inspect tool calls, handle approvals, follow subtasks, and export a report for each run.

A persistent **Core** manages execution and sessions, with **Web / CLI / TUI** interfaces, **Loop / LangGraph** engines, and **Local / Kubernetes** tool environments.

<a id="demo"></a>

## 📸 Demo

**From a task description to results you can inspect and export.**

![KitAgent 46-second demo: submit a task, approve tool calls, inspect results, and export the report](docs/assets/web-workbench-demo.gif)

<p align="center">
  Sessions · Multi-turn chat · Tool timeline · Run reports<br />
  <a href="docs/assets/web-workbench-overview.png">Full-resolution screenshot</a> · <a href="https://raw.githubusercontent.com/zed123214/kitagent/main/docs/assets/web-workbench-demo.webm">Download the full video</a> · <a href="docs/web-workbench.md">Launch the workbench</a>
</p>

For a repository check, start with:

> Inspect the sample Python repository, run its check script, and write a report.

| Step | What you see in the workbench |
| --- | --- |
| **① Describe the goal** | Create a session and submit a task in natural language. |
| **② Follow execution** | Read agent responses, tool arguments, execution status, and output. |
| **③ Make decisions** | Approve or reject calls, and remember tool grants for the session. |
| **④ Use the result** | Review the conclusion, tools, and approvals; export the report and continue chatting. |

<details>
<summary><strong>See tool calls and human approval</strong></summary>

![KitAgent approval view: inspect the pending tool and arguments, then approve or reject](docs/assets/web-workbench-approval.png)

Choose Read-only, Ask as needed, or Auto-approve for a session. View and revoke remembered tool grants from the permission menu.

</details>

<p align="center"><sub>Built-in offline demo · Scripted model responses + live tool execution · <a href="docs/web-workbench.md#无-api-key-的真实工具演示">Try it locally</a></sub></p>

<a id="operator-demo"></a>

### 🧪 Workflow demo: develop and optimize Ascend operators with an agent

**Turn a correct operator into an optimization you can explain, validate, and deliver.** Equal covers development from input semantics to community acceptance. SparseFlashAttentionGrad covers algorithm selection, Cube / Vector coordination, bottleneck diagnosis, and rejected candidates.

This workflow combines existing project records with methods presented in operator-competition talks. Results come from the original archives; there is no end-to-end KitAgent run record for these operators yet. The GIF above remains the repository-check demo.

**Follow the workflow:** establish the contract and environment → map computation and data movement → implement a correct baseline → compare candidates → measure and validate → freeze the delivery. Diagnose build or numerical failures first, then use performance evidence to decide which changes to keep.

| Stage | Question for the agent | Output to review |
| --- | --- | --- |
| **① Set up** | What are the interface, dtypes, shapes, hardware, CANN version, and acceptance criteria? | Input contract, environment inventory, baseline source version, and executable validation commands. |
| **② Design** | What are the dependencies and data movements? Which work belongs on the Host, AIC (matrix core), or AIV (vector core)? | Computation steps, transfer paths, task ownership, and an algorithm comparison. |
| **③ Implement** | Can the minimal correct path build, run, and match the reference? | A runnable baseline, boundary tests, and a diagnosis of the first failure. |
| **④ Optimize** | Is the cost in indexing, computation, transfers, synchronization, or uneven work? | A testable hypothesis, a diff, admission conditions, and a fallback. |
| **⑤ Decide** | Is it faster on matching inputs and environments? Do other scenarios regress? | A correctness matrix, paired timings in both orders, stage evidence, and a keep/revert decision. |
| **⑥ Deliver** | Does the integrated version still pass, and how can someone verify it? | Frozen source, build and loaded-library identities, input hashes, raw reports, and untested scope. |

<details>
<summary><strong>Demo 1 · Equal: connect semantics, implementation, and acceptance</strong></summary>

**Start with the contract.** Equal compares corresponding elements of two broadcastable tensors and produces BOOL output. For example, shapes `[2,1]` and `[1,3]` produce `[2,3]`; output coordinates must map to each input rather than simply comparing matching addresses.

**Explain the implementation choices.** The Host compresses broadcast axes, precomputes effective strides, and divides work across cores. The kernel moves and compares contiguous segments, reusing UB data for eligible broadcast patterns.

ACLNN validates the interface and performs required input/output adaptation. INT64 uses exact high/low 32-bit comparisons to avoid lossy conversion.

Submit each prompt in the workbench and review its output before continuing:

> **Turn 1 — Contract and baseline.** Read the Equal specification, source, and tests; identify entry points and versions. Describe dtypes, broadcasting up to 8 dimensions, and outputs. Explain address mapping with a two-sided broadcast example. List NaN, signed-zero, INT64-boundary, and tail tests, and separate Host Tiling, kernel, and ACLNN responsibilities. Establish a build and correctness baseline.

> **Turn 2 — One change and its counterexamples.** Select a remaining bottleneck supported by evidence in the correct baseline. Explain existing axis compression, contiguous segments, and caching. Propose one change, its admission conditions, and inputs that might regress. Preserve the baseline and fallback, validate affected semantics and boundaries, and distinguish source-based reasoning from device measurements.

> **Turn 3 — Paired acceptance and delivery.** Verify the libraries and task types actually used by custom and builtin. Compare matching inputs. Separate kernel device time from full interface time when the latter is measured. Report versions, environment, warm-ups, sampling, thresholds, and failures. Without an NPU, supply reproduction commands and pending checks. Freeze the accepted source and export the run report.

**Historical delivery:** records for source commit `763a5cf5` report **306/306 correctness passes** and **306/306 performance-threshold passes**. Project documentation records the merge through [cann/ops-math PR #5425](https://gitcode.com/cann/ops-math/pull/5425/discuss).

Timing used 5 warm-ups and the median of 10 device-task measurements. For builtin time B and custom time C, acceptance requires C ≤ B + 3 μs when B < 15 μs, otherwise B/C ≥ 0.95.

Of the stress cases, 131 reused traceable historical builtin baselines; 4 used two paired reruns of both implementations. Passing does not mean every case is faster or that both A2 and A3 hardware independently ran the entire suite.

</details>

<details>
<summary><strong>Demo 2 · SparseFlashAttentionGrad: from dependencies to evidence-backed optimization</strong></summary>

**Preserve the mathematics before changing the computation.** Sparse indices can repeat: `[2,0,2,3]` has counts `[1,0,2,1]` for keys `[0,1,2,3]`. Each repeated occurrence contributes to the gradients; deduplication alone changes the result.

For the main path without RoPE and with a separate Value input, let `α` be the scale, `m/z` the matching forward stabilization maximum/normalization sum, and `count` the valid-index multiplicity. Aggregating by unique key gives:

```text
score = Q @ Kᵀ                    dP = dOut @ Vᵀ
P = exp(α · score - m) / z         delta = rowsum(dOut · Out)
W = count · P                     G = W · (dP - delta)
dQ = α · G @ K                    dK = α · Gᵀ @ Q
dV = Wᵀ @ dOut
```

These equations explain dependencies; the implementation computes in blocks. RoPE, optional Value, invalid indices, and length boundaries still require contract-specific handling.

AIC performs matrix products, while AIV handles counts, coefficients, and vector reductions. Buffer placement, transfers, publication, and waits must be traced to the selected source version.

**Make each optimization a question you can test:**

| Question | Candidates and tradeoffs | Evidence required |
| --- | --- | --- |
| How should repeated indices be counted? | Compare scalar counting with sorted cumulative-boundary differences. Direct binary search, partitioned binary search, and merging are candidates to evaluate against index length, key range, repetition, and UB budget. | Matching counts, full-gradient correctness, and total sorting/search/merge cost. Listing a candidate does not mean this project implements it or proves it faster. |
| Why are matrix cores waiting? | Separate computation, transfers, readiness publication, and waits. Check whether coordination competes with the previous round's dK / dV work on the same core. | Device markers or profiling timelines by core and stage, with clock, synchronization, and instrumentation overhead described. An API envelope is not a direct measure of hardware busy time. |
| Are five slabs balanced? | For 512 rows split as 128/128/128/64/64, inspect ownership of dQ and dK / dV together, rather than relying on row counts. | Per-core work, the final critical path, output ownership, complete reductions, and matched paired timing. |
| Does the change work beyond a few inputs? | Build a matrix across dtype, mode, RoPE, Value, shape, tails, and index distributions. Keep explicit admission conditions and a fallback. | Separate official public cases, self-generated extensions, and untested scope. Record compilation and numerical device validation separately. |

**Four prompts for the workbench:**

> **Turn 1 — Dependencies and candidates.** Read the baseline, contract, and golden. Map the forward saved values to dQ/dK/dV and explain repeated-index contributions. List the current counting method, two alternatives, and their admission conditions. Mark implemented and proposed work separately. Establish correctness and a test matrix; select algorithms by input properties, not case IDs.

> **Turn 2 — Measurements and hypotheses.** Read profiling or marker records and organize a timeline by AIC/AIV and compute, transfer, publish, and wait stages. Distinguish full-call time, kernel time, and instrumentation envelopes. Identify the critical path. Label each conclusion as measured, inferred from source, or pending, and explain how to control instrumentation effects.

> **Turn 3 — Change and challenge it.** Explain the evidence behind the initial five-slab regression, including dK/dV work on short-slab cores. Test one mapping hypothesis while preserving output ownership and complete reductions. Validate every gradient present and the affected branches. Repeat baseline→candidate and candidate→baseline measurements. Keep slower results; combined changes do not establish an individual mechanism's gain.

> **Turn 4 — Integrate and freeze.** Prioritize remaining work by correctness, expected benefit, validation cost, and regression risk; reserve time for package acceptance. Freeze candidates, unify interfaces, Host routing, and fallback, then rerun integration checks. Archive the official submission, prototypes, and refactor separately, binding source hashes, vendor, input hashes, reports, and untested scope.

**One recorded optimization cycle:**

| Decision | Observation | Next step |
| --- | --- | --- |
| Reject the initial five-slab prototype | Time increased **4.76% / 1.47%** in the two orders; stage records placed the dK / dV tail on short-slab cores. | Redistribute reduction work and retain the regression record. |
| Promote the revised historical prototype | On 910B3: **280.17 → 258.99 μs** forward, **275.31 → 259.71 μs** reverse, reducing time by **7.56% / 5.67%**. | Evaluate against its own contiguous-C1 control before integration. Evidence covers these two orders and combined changes, with no final single-mechanism ablation. |
| Validate the post-competition R5 refactor | On 910B4 / CANN 8.5.0: **56 FP16 correctness reports and 112 poison checks** across 28 scenarios and two versions; 180 Event reports across 15 geometries yielded a geometric mean candidate/original median-time ratio of **0.99555**. | Passed the predefined no-material-regression thresholds; BF16 coverage was template compilation only. |

Official submission `1041451` is **Pass / 47.21 points** in the archived **October 31, 2026** ranking. Prototype gains, official scores, and R5 regression results use separate measurement scopes.

</details>

<details>
<summary><strong>Collaboration demo · A lead task owns the contract; subtasks return reviewable candidates</strong></summary>

Inspired by the lead/worker split in the talks, independent research can use [Subagents](docs/skills-subagents-mcp.md), with the lead task owning interfaces, acceptance, and integration.

This is a suggested workflow, not a claim that KitAgent automatically isolates Git repositories or merges candidates.

| Role | Responsibility | Return to the lead |
| --- | --- | --- |
| Lead | Fix the baseline, shared interfaces, tests, and time budget; schedule device measurements and choose candidates. | Candidate list, integrated version, and acceptance decision. |
| Algorithm subtask | Study broadcast mapping or counting, comparing conditions and costs. | Source evidence, candidate differences, counterexamples, and fallback conditions. |
| Pipeline subtask | Study transfers, synchronization, and cross-core work allocation. | Timeline evidence, a critical-path hypothesis, and a validation plan. |
| Validation subtask | Extend the test matrix, verify loaded libraries, and organize paired reports. | Per-case results, failures, and source/input bindings. |

For concurrent edits, explicitly prepare a separate checkout or Git worktree for each candidate and assign its path, allowed files, and handoff format. Subagents in one session share the tool workspace by default.

Serialize comparative measurements on a shared NPU so candidates do not interfere with one another.

> **Lead-task prompt.** Fix the input contract, baseline commit, validation commands, and acceptance criteria. Split algorithm analysis, pipeline analysis, and test-matrix design into independent read-only subtasks first. Prepare separate candidate directories before edits. Require each candidate to return its diff, admission conditions, correctness/performance evidence, and failures. Integrate, run the full regression suite, and freeze the delivery through the lead task.

</details>

**Try it in KitAgent:** follow [Quick Start](#quick-start). Supply tool-accessible paths to source, specifications, golden, and historical reports, and describe the available hardware. Submit the prompts using a live model, inspect tool calls, handle session approvals, and export reports.

Device validation needs a compatible Ascend NPU, driver, CANN, and test tools; the default Local / kind environment does not supply that hardware.

**Without an NPU:** demonstrate contract analysis, source explanations, candidate comparison, and offline checks of existing reports. Deliver a test matrix and reproduction commands; device correctness, performance, and synchronization remain pending.

The original project materials are not distributed with KitAgent and must be supplied before using these cases.

<details>
<summary><strong>Sources, method references, and result scope</strong></summary>

Historical sources: `Equal算子开发流程与面试讲解.md` (September 16, 2026, chapters 3, 11, and 12), and `星辰杯_答辩材料包_2026-11-06`.

SparseFlashAttentionGrad figures map to E01 ranking, E02 correctness status, E03 paired comparison, E11 prototype decision, and the initial five-slab record. The original materials are not distributed with this repository.

Method references are photographs of operator-competition talks covering algorithm selection, marker-based pipeline timelines, computation flow, “Agentic Ops Develop,” problem formulation, dataset partitioning, and allocation of time and submission budget.

Some slides are obscured; only readable methodological ideas are used. The photographs and other presenters' experimental results are not included as this project's achievements.

The methods are adapted here as KitAgent collaboration examples. The slides' `asc-setup / asc-design / asc-implement / asc-optimize / asc-profile / asc-loop / asc-debug / asc-submit` commands belong to an external `asc-op-dev` example and are not built into KitAgent.

Algorithm candidates and expanded test matrices describe proposed work, not existing implementations or completed test coverage.

The project archives disclose AI assistance with research, edits, experiment orchestration, and evidence organization. They provide neither an end-to-end KitAgent run record nor a human-hours comparison; no Agent productivity gain is claimed.

The new methodological guidance does not change the measurement scope of the historical results above.

</details>

<a id="features"></a>

## ✨ Features

### One Core, three interfaces

Chat, approve calls, and inspect reports in the **Web workbench**. Submit tasks and integrate scripts through the **CLI**, or work in the terminal with the **Textual TUI**. All three interfaces share the runtime protocol, with Core managing task and session state.

The Web gateway maintains its Core connection, so you can refresh the browser and keep following an active task.

### Execution you can inspect

Follow streaming responses and a tool timeline to see which tools ran, their inputs, outputs, and timing. Each run records events in `events.jsonl` for replay; correlation IDs connect parent and child tasks.

Export a run report with the conclusion, tool output, and approval records for review or sharing.

### Collaboration and tool approval

Add requirements and adjust direction through multi-turn conversation. Use approval cards to decide whether a tool should run, remember a tool grant for the session, or revoke it from the permission menu.

Built-in tools and MCP tools share registration, argument validation, permission policies, and execution records.

### Session memory and extensions

Keep conversation history, long-term notes, and compact summaries across turns. Package workflows as Markdown **Skills**, connect external tools through **MCP**, and delegate independent work to **Subagents** with their own contexts.

### Engine choice and durable recovery

Use the default **Loop** engine for model–tool execution or **LangGraph** for explicit node orchestration. With **Graph + SQLite + Local**, save checkpoints and approval interrupts, resume after a Core restart, and reuse recorded tool results.

### Kubernetes workspaces per session

Use **Local** tools for development, or enable **Kubernetes Sandbox** to create a Pod on demand for each session. Turns and subagents within a session share the workspace, with resource limits, network policies, idle reclamation, and cleanup on close.

<a id="architecture"></a>

## 🏗️ Architecture

![KitAgent architecture: Web, CLI, and TUI connect to Core, sharing engines, tools, permissions, and events across model providers, Local and Kubernetes environments, and extensions](docs/assets/architecture.en.svg)

<p align="center">
  <a href="docs/assets/architecture.en.png">High-resolution PNG</a> · <a href="docs/assets/architecture.drawio">Editable draw.io source</a> · <a href="docs/architecture.md">Architecture details</a>
</p>

**Follow a task:** submit a goal → Core creates a run → engine calls the model → approve and execute tools → stream events → commit the session result.

| Layer | Technology and responsibility |
| --- | --- |
| **Interfaces** | React 19, TypeScript, assistant-ui, Textual; Web, CLI, and TUI. |
| **Transport** | FastAPI and WebSocket; the gateway connects to Core through JSON-RPC 2.0 / NDJSON TCP. |
| **Runtime** | Python 3.12, asyncio, Pydantic v2; sessions, tasks, permissions, and events. |
| **Engines** | Loop / LangGraph; shared model, tool, and session interfaces. |
| **Model integration** | Anthropic Provider; server-side model and API key configuration. |
| **Tool environments** | Local / Kubernetes; command execution and file operations. |
| **Storage and extensions** | JSONL, Markdown, SQLite; replay, memory, recovery, Skills, and MCP. |

## 📊 Measured Results

Sandbox validation completed on **September 9, 2026**, using **single-node kind / Kubernetes v1.36.4 / Cilium 1.20.1**, an offline provider, and preloaded images.

| Check | Result |
| --- | --- |
| **Live-cluster validation** | M1 **13/13**, M2 **442/442**, across 12 experiment categories. |
| **Concurrent session isolation** | **20** sessions, **200** cross-session read/write probes, **0** leaks. |
| **Creation and cleanup** | **100/100** completed, **0** resources left at the end. |
| **Sandbox cold start** | **3.52 s** p95 to Ready, 30 serial samples. |
| **Execution overhead after Ready** | **19.26 ms** p95, 100 samples; Core duration minus Worker command duration. |

[Sandbox configuration and validation walkthrough →](docs/kubernetes-sandbox.md#构建渲染与后续验收)

<a id="quick-start"></a>

## 🚀 Quick Start

Run these commands in **Bash on Linux / WSL2**. Install **Python 3.12** and [uv](https://docs.astral.sh/uv/). The Web workbench also needs **Node.js 22.12+** to build its frontend.

### 1. Install and configure the model

```bash
git clone https://github.com/zed123214/kitagent.git
cd kitagent
uv sync --frozen --extra web
cp .env.example .env
```

Edit `.env` with your model configuration:

```dotenv
ANTHROPIC_API_KEY=your-api-key
AGENTRT_LLM_DEFAULT_MODEL=claude-sonnet-4-6
```

### 2. Build the workbench

```bash
cd frontend
npm ci
npm run build
cd ..
```

### 3. Start Core and the Web gateway

Open two terminals in the repository root.

**Terminal one · Core**

```bash
uv run --frozen --extra web agentrt-core
```

**Terminal two · Web gateway**

```bash
uv run --frozen --extra web agentrt-web
```

Open the gateway's startup link (`http://localhost:8765/#bootstrap=…`), create a session, and submit your first task. The default is **Loop + Local**, with tools running in Core's working directory.

### Prefer the terminal?

With Core running, use the CLI or TUI in another terminal:

```bash
# Check the connection
uv run --frozen --extra web agentrt ping

# Submit a task
uv run --frozen --extra web agentrt run --goal "Read the project structure and summarize the main modules"

# Open the terminal interface
uv run --frozen --extra web agentrt-tui
```

<details>
<summary><strong>No API key needed: try the engine and cross-process recovery</strong></summary>

Run the offline model → tool → model example:

```bash
uv run --frozen --extra graph python examples/graph_offline_demo.py
```

Resume a task after a Core restart and reuse completed tool results:

```bash
uv run --frozen --extra graph-sqlite python examples/durable_recovery_demo.py
```

For an offline browser demo, see the [workbench guide](docs/web-workbench.md#无-api-key-的真实工具演示).

</details>

### Choose a runtime mode

| Mode | Use case | Guide |
| --- | --- | --- |
| **Loop + Local** | Web workbench, local development, and everyday tasks | [Workbench](docs/web-workbench.md) · [Runbook](RUNBOOK.md) |
| **Graph + Memory** | Explicit node orchestration and in-process session continuation | [Graph engine](docs/graph-engine.md) |
| **Graph + SQLite + Local** | Core restart recovery and durable human approval | [Recovery](docs/durable-recovery.md) |
| **Loop / Graph Memory + Kubernetes** | Container workspaces per session | [Sandbox deployment](docs/kubernetes-sandbox.md) |

<a id="docs"></a>

## 📚 Documentation

| I want to… | Start here |
| --- | --- |
| Use the browser workbench | [Web workbench](docs/web-workbench.md) |
| Configure and run the project | [Runbook](RUNBOOK.md) |
| Follow task execution | [Architecture](docs/architecture.md) · [Agent Loop](docs/agent-loop.md) |
| Use Graph and recovery | [Graph engine](docs/graph-engine.md) · [Durable recovery](docs/durable-recovery.md) |
| Deploy Kubernetes sandboxes | [Deployment and validation](docs/kubernetes-sandbox.md) |
| Configure permissions and memory | [Tool permissions](docs/tool-permissions.md) · [Session memory](docs/session-memory.md) |
| Extend workflows and tools | [Skills / Subagents / MCP](docs/skills-subagents-mcp.md) |
| Build a client or contribute | [Wire protocol](WIRE_PROTOCOL.md) · [Contributing](CONTRIBUTING.md) |

## 🤝 Contributing

Share use cases, report bugs through [Issues](https://github.com/zed123214/kitagent/issues), or open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and checks.

If KitAgent helps with your work, give it a **Star** and share what you built with it.

## 📄 License

[MIT](LICENSE)
