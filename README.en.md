<div align="center">

<h1>KitAgent</h1>

<p><strong>Bring an AI agent into development, testing, and performance optimization</strong></p>

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

[Demo](#demo) · [Operator Optimization](#operator-demo) · [Features](#features) · [Architecture](#architecture) · [Quick Start](#quick-start) · [Documentation](#docs)

<p><a href="https://github.com/zed123214/kitagent"><strong>⭐ Star KitAgent</strong></a> · <a href="#quick-start">Get started</a> · <a href="#operator-demo">Explore operator optimization</a></p>

</div>

---

KitAgent is an open-source AI agent runtime and visual workbench. Describe a development goal; let the agent read code, edit files, and run commands.

Inspect tool output, handle approvals, and keep working in the same conversation.

Use it to connect analysis, experiments, and delivery, from repository checks to operator optimization. The **Equal** and **SparseFlashAttentionGrad** walkthroughs explain how to find bottlenecks, organize data, and distribute computation.

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

## 🧪 Optimize operators with an agent: Equal to SparseFlashAttentionGrad

An operator maps a mathematical operation onto data movement and hardware instructions. Comparing two values is simple. Comparing entire tensors also takes broadcast indexing, tiled transfers, and work across cores.

Start with Equal to learn broadcasting and buffer reuse. Then explore matrix/vector cooperation and load balancing through SparseFlashAttentionGrad.

Use KitAgent to carry the analysis, edits, tests, and experiment reports through one conversation.

### Equal: organize the data behind a comparison

Equal compares corresponding tensor values and returns BOOL. Inputs shaped `[2,1]` and `[1,3]` produce `[2,3]`. Address mapping lets each output tile read the corresponding values from the original inputs.

**Precompute repeated indexing work.** On the Host, merge adjacent axes with matching broadcast patterns and calculate strides. The kernel locates a contiguous segment, then compares its elements in batches.

**Reuse what you load.** Choose tile sizes from dtype and the UB on-chip memory budget. Account for inputs, outputs, and scratch space. Cache scalars, broadcast planes, and reusable tail rows; assign output regions across cores.

**Test numerical behavior.** Cover NaN, signed zero, and infinities. Compare INT64 through its high and low 32-bit components to retain all integer information. Connect validation, execution, and output handling through ACLNN.

| Stage | Method | Result |
| --- | --- | --- |
| Specification and baseline | Define behavior with broadcast examples and special values. | Input/output contract, CPU reference, and test matrix. |
| Tiling and kernel | Precompute indexing on the Host; compare and reuse tiles on the device. | Axis compression, multicore tiling, vector comparison, and buffer reuse. |
| Validation and delivery | Freeze a version, compare outputs, and collect per-case results. | **306/306 correctness passes**; code merged through [cann/ops-math PR #5425](https://gitcode.com/cann/ops-math/pull/5425/discuss). |

### SparseFlashAttentionGrad: balance the complete pipeline

Sparse Attention backward computes `dQ / dK / dV` alongside index processing, coefficients, and gradient accumulation. Plan when each block becomes ready, which core consumes it, and where reductions finish.

**Batch repeated-index counts.** Indices `[2,0,2,3]` have counts `[1,0,2,1]` for keys `[0,1,2,3]`. Preserve each occurrence in the gradient. Sorting and cumulative-boundary differences provide a batch approach to counting.

**Separate computation and coordination.** AIC matrix cores perform matrix multiplication. AIV vector cores handle counts, coefficients, and readiness aggregation. Plot production, publication, waits, and gradient work on a timeline.

**Balance all work assigned to each core.** A 512-row split of `128 / 128 / 128 / 64 / 64` also needs to account for dK / dV reductions. A short-slab core can finish last when it has more reduction work.

The following 910B3 five-slab prototype experiment shows how measurements guide the next edit:

| Iteration | Observation | Method |
| --- | --- | --- |
| Initial split | Time rose **4.76% / 1.47%** in the two orders, with the dK / dV tail on short-slab cores. | Account for query work and gradient reductions together. |
| Revised ownership | **280.17 → 258.99 μs** forward; **275.31 → 259.71 μs** reverse. | Redistribute reductions; time fell **7.56% / 5.67%**. |
| Integration checks | R5 produced **56 FP16 correctness reports and 112 poison checks** on 910B4 / CANN 8.5.0. | Check complete gradients, output writes, and input immutability. |

Locate the tail, redistribute query and reduction work together, then compare under matching conditions. Start the next iteration from the updated timeline.

### Four optimization steps from these cases

| Step | Question | Action |
| --- | --- | --- |
| **① Measure** | Where does execution spend its time? | Establish a baseline and inspect profiling timelines for compute, transfers, and waits. |
| **② Reduce transfers** | How often is the same data read or written? | Fuse adjacent computation, tile to fit on-chip memory, and reuse inputs and intermediate results. |
| **③ Schedule work** | Which cores are busy, and which are waiting? | Assign matrix and vector work, overlap transfers with computation, and balance the full workload. |
| **④ Compare** | What changed after the edit? | Check reference outputs, repeat matched baseline/candidate measurements, and choose the next experiment. |

Further reading: Xiaolin Coding's [Star Cup operator-optimization walkthrough](https://mp.weixin.qq.com/s/Sr8wVJQw0Pt6xZSOtdHp2w) explains data movement, tiling, reuse, and task allocation.

### Run the workflow in KitAgent

Provide source, specifications, a reference implementation, and test commands. Continue analysis, edits, and validation in one session. Inspect tool output, handle approvals, and export the run report.

| Turn | Agent task | What you review |
| --- | --- | --- |
| **Understand** | Explain inputs, outputs, dependencies, and build/test entry points. | Computation steps, validation commands, and a correct baseline. |
| **Diagnose** | Read profiling and compare algorithms, transfers, and task mappings. | Time distribution, a hypothesis, and candidate changes. |
| **Experiment** | Implement a candidate and run correctness checks and paired timing. | Code diff, per-case results, and before/after times. |
| **Iterate** | Keep or revise the candidate, then run integration checks. | Delivery version, experiment conclusions, and run report. |

<details>
<summary><strong>Copy this task to start an optimization</strong></summary>

```text
Help optimize the operator in this workspace.

Read its specification, source, and reference implementation.
Map inputs, outputs, dependencies, build commands, and tests.
Establish correctness and performance baselines.

Find time spent in computation, transfers, indexing, and waits.
Choose one optimization, explain the overhead it addresses,
preserve the baseline, and implement the candidate.

Check outputs on identical inputs. Repeat measurements in
baseline→candidate and candidate→baseline order.
Summarize the code changes, correctness, and timing differences.
Use the results to choose the next experiment and write a report.
```

For larger tasks, use [Subagents](docs/skills-subagents-mcp.md) to study algorithms, pipelines, and tests. Let the lead task schedule device measurements and integrate the changes. Save repeatable steps as Skills.

</details>

**Ready for your first experiment?** [Launch the workbench](#quick-start) and bring your own task. Give KitAgent a [**⭐ Star**](https://github.com/zed123214/kitagent) to support the project and find it again for your next experiment.

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

Want an AI agent for your own development tasks? Give KitAgent a [**⭐ Star**](https://github.com/zed123214/kitagent) and share your experiments or use cases in Issues.

## 📄 License

[MIT](LICENSE)
