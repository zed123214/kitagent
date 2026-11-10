<div align="center">

<h1>KitAgent</h1>

<p><strong>把开发任务交给 Agent，查看过程、审批工具、导出报告</strong></p>

<p>开源 AI Agent 运行时与可视化工作台</p>
<p><sub>对话驱动任务 · 实时工具追踪 · 人工审批 · 会话记忆 · Kubernetes 沙箱</sub></p>

<p>
  <a href="https://github.com/zed123214/kitagent/actions/workflows/ci.yml"><img src="https://github.com/zed123214/kitagent/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12" /></a>
  <a href="frontend/package.json"><img src="https://img.shields.io/badge/React-19-149ECA?logo=react&logoColor=white" alt="React 19" /></a>
  <a href="docs/kubernetes-sandbox.md"><img src="https://img.shields.io/badge/Kubernetes-Sandbox-326CE5?logo=kubernetes&logoColor=white" alt="Kubernetes Sandbox" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-F5C542" alt="MIT License" /></a>
</p>

**中文** · [English](README.en.md)

[产品演示](#demo) · [核心能力](#features) · [快速开始](#quick-start) · [系统架构](#architecture) · [算子案例](#operator-demo) · [文档导航](#docs)

<p><a href="#quick-start">开始使用</a> · <a href="docs/web-workbench.md#无-api-key-的真实工具演示">无需 API Key 体验演示</a> · <a href="docs/architecture.md">阅读实现</a></p>

</div>

---

KitAgent 面向想使用、学习或扩展 AI Agent 的开发者。你描述任务，Agent 阅读代码、修改文件、执行命令；你在自己的工作台中查看工具输入输出、决定是否批准调用，并导出包含结论和执行记录的报告。

你可以从这三件事开始：

- **完成开发任务**：让 Agent 检查仓库、执行测试、整理报告，在同一会话里补充要求、继续修改。
- **学习 Agent 如何运行**：沿着任务、工具调用、人工审批和事件记录阅读实现，再查看会话记忆、持久化恢复与沙箱的设计。
- **扩展自己的工作流程**：用 Markdown Skills 保存步骤，通过 MCP 接入工具，用 Subagents 拆分独立子任务。

[先看操作演示](#demo)，或直接[启动工作台](#quick-start)；希望研究实现，可以从[系统架构](#architecture)进入。

<a id="demo"></a>

## 📸 产品演示

**从算子规格，到实现、正确性验证与性能实测。**

![KitAgent 算子开发演示：实现 Equal、审批测试、对比实测性能并导出报告](docs/assets/equal-operator-demo.gif)

<p align="center">
  Equal 算子开发 · 广播与边界验证 · 基线性能对比 · 开发报告<br />
  <a href="docs/assets/equal-operator-overview.png">查看高清截图</a> · <a href="https://raw.githubusercontent.com/zed123214/kitagent/main/docs/assets/equal-operator-demo.webm">下载完整视频</a> · <a href="docs/web-workbench.md">启动工作台</a>
</p>

以 `Equal` 算子开发为例：

> 开发 Equal 算子，支持标量广播，验证正确性并对比基线性能，生成开发报告。

| 步骤 | 你在工作台中看到的内容 |
| --- | --- |
| **① 确认规格** | 读取 Equal 规格，明确等长比较、标量广播与边界语义。 |
| **② 编写实现** | 审批写入算子实现，将等长与广播路径分开，移除逐元素取模索引。 |
| **③ 验证与实测** | 审批运行测试，验证 75 个用例；对三组输入预热 3 次、采样 9 次，对比中位耗时。 |
| **④ 交付报告** | 审批保存开发报告，读回核对结果；导出结论、工具证据和审批记录。 |

<details>
<summary><strong>展开查看：工具调用与人工审批</strong></summary>

![KitAgent 审批界面：查看待执行工具及参数，选择批准或拒绝](docs/assets/equal-operator-approval.png)

工作台提供「只读 / 按需询问 / 自动批准」三种会话权限模式，并支持查看和撤销已记住的工具授权。

</details>

<p align="center"><sub>内置离线演示 · 脚本化模型响应 + 实际工具执行 · <a href="docs/web-workbench.md#无-api-key-的真实工具演示">在本机体验</a></sub></p>

> 如果你想搭建自己的 Agent，或研究工具调用、人工审批与会话管理的实现，欢迎点右上角 **⭐ Star**，收藏这套源码、运行示例和设计文档。

### LangGraph 实战：算子优化状态机

把一次算子优化组织成可追踪的工作流：**制定计划、验证候选、评估性能、诊断重试、审核交付**。每个节点更新共享状态，下一步由验证结果与审核决定驱动。

```mermaid
flowchart LR
    A[plan 任务规划] --> B[validate 精度检查]
    B -->|通过| C[benchmark 性能评估]
    B -->|失败| D[diagnose 诊断与迭代]
    C -->|退化| D
    D -->|继续迭代| B
    D -->|达到上限| F[fallback 保留基线]
    C -->|达标| E[review 审核中断]
    E -->|approve| G[deliver 接受候选]
    E -->|reject| F
    G --> H[report 输出报告]
    F --> H
```

| LangGraph 场景 | 示例实现 | 你能看到什么 |
| --- | --- | --- |
| 有状态工作流 | `StateGraph` 保存阶段、候选序号、决策历史和选中版本 | 每轮结果随状态流转，失败记录持续保留 |
| 条件路由 | 精度与性能结果决定后继节点 | 精度失败跳过计时，性能退化进入诊断 |
| 迭代与终止 | `max_attempts` 控制候选轮次 | 预算耗尽后保留基线并生成报告 |
| 审核与恢复 | `interrupt()` 暂停，`Command(resume=...)` 传回决定 | 批准后交付，拒绝后保留基线 |
| 检查点 | `InMemorySaver` 按 `thread_id` 保存进程内状态 | 从审核节点续跑，已完成的评估保持原样 |
| 工具集成与观测 | KitAgent Graph 引擎调用工作流工具，业务图输出节点更新 | 同时观察 `model / kit_tools` 与业务阶段，导出 JSON 报告 |

**运行一次完整流程：**

```bash
uv run --frozen --extra graph python examples/operator_workflow_demo.py --review approve --output operator-report.json
```

切换 `--review reject` 查看审核拒绝分支；设置 `--max-attempts 1` 查看提前结束与基线保留。`--review` 指定本次演示在审核检查点恢复时使用的决定。

内置案例使用 SparseFlashAttentionGrad 的归档实验记录：五分片初稿退化后进入下一轮，重分配候选通过评估后进入审核。报告保留各候选的对照耗时、变化率、来源、审核决定及最终版本。

[查看状态机代码](examples/operator_workflow_demo.py) · [查看分支与恢复测试](tests/unit/test_operator_workflow_demo.py) · [了解 KitAgent Graph 引擎](docs/graph-engine.md)

<a id="features"></a>

## ✨ 核心能力

### 一个 Core，三种交互方式

在 **Web 工作台**中对话、审批和查看报告，在 **CLI** 中提交任务与接入脚本，在 **Textual TUI** 中进行终端交互。三种入口共用运行时协议，任务执行和会话状态由 Core 管理。

Web 网关持续连接 Core，刷新浏览器后可以继续观察正在执行的任务。

### 看得见的执行过程

通过流式回复和工具时间线查看任务进展：调用了什么工具、输入是什么、结果如何、用了多久。每次运行的事件保存到 `events.jsonl`，支持历史回放；父任务与子任务通过关联标识串联。

运行报告汇集本轮结论、工具输出和审批记录，方便复盘与分享。

### 多轮协作与工具审批

通过多轮对话补充要求、调整任务方向；通过审批卡片决定工具是否执行。你可以为当前会话记住某个工具的授权，也可以从权限菜单中撤销。

工具注册、参数校验、权限策略和执行记录采用同一套机制，内置工具与 MCP 工具都能接入。

### 会话记忆与能力扩展

会话历史、长期笔记和压缩摘要分层保存，让 Agent 在后续轮次中沿用已有信息。使用 Markdown **Skills** 封装工作流程，通过 **MCP** 连接外部工具，将独立子任务交给拥有各自上下文的 **Subagents**。

### 执行引擎与持久化恢复

默认 **Loop** 引擎运行模型与工具循环；可选 **LangGraph** 引擎提供显式节点编排。启用 **Graph + SQLite + Local** 后，可保存执行检查点与审批中断，在 Core 重启后续接任务，并复用已经记录的工具结果。

### 按会话组织的 Kubernetes 沙箱

本地开发使用 **Local** 工具环境；需要独立工作区时，启用 **Kubernetes Sandbox**，为每个会话按需创建 Pod。同一会话中的多轮任务与子 Agent 共用工作区，支持资源限制、网络策略、空闲回收和关闭清理。

<a id="architecture"></a>

## 🏗️ 系统架构

![KitAgent 系统架构：Web、CLI、TUI 连接 Core，通过共享的引擎、工具、权限和事件机制接入模型、本地环境、Kubernetes 沙箱与扩展能力](docs/assets/architecture.svg)

<p align="center">
  <a href="docs/assets/architecture.png">高清 PNG</a> · <a href="docs/assets/architecture.drawio">可编辑 draw.io 源文件</a> · <a href="docs/architecture.md">架构设计详解</a>
</p>

**任务路径：** 提交目标 → Core 创建任务 → 执行引擎调用模型 → 工具审批与执行 → 事件推送 → 会话结果。

| 层次 | 技术与职责 |
| --- | --- |
| **交互层** | React 19、TypeScript、assistant-ui、Textual；提供 Web、CLI 与 TUI。 |
| **连接层** | FastAPI、WebSocket；网关通过 JSON-RPC 2.0 / NDJSON TCP 连接 Core。 |
| **运行时** | Python 3.12、asyncio、Pydantic v2；管理会话、任务、权限与事件。 |
| **执行引擎** | Loop / LangGraph；复用模型、工具和会话接口。 |
| **模型接入** | Anthropic Provider；通过服务端配置设置模型与 API Key。 |
| **工具环境** | Local / Kubernetes；承载命令执行与文件操作。 |
| **持久化与扩展** | JSONL、Markdown、SQLite；支持事件回放、记忆、恢复、Skills 与 MCP。 |

## 📊 工程实测

2026-09-09，在 **单节点 kind / Kubernetes v1.36.4 / Cilium 1.20.1** 环境完成沙箱验收，使用离线 Provider 与预加载镜像。

| 验证项 | 结果 |
| --- | --- |
| **真实集群验收** | M1 **13/13**，M2 **442/442**，覆盖 12 类实验。 |
| **并发会话隔离** | **20** 个 Session，**200** 次跨会话读写探测，泄漏 **0**。 |
| **创建与回收** | **100/100** 完成，最终资源残留 **0**。 |
| **沙箱冷启动** | 到 Ready 的 p95 为 **3.52 s**，30 个样本、串行采样。 |
| **就绪后执行开销** | p95 **19.26 ms**，100 个样本，按 Core 总耗时减 Worker 命令耗时计算。 |

[查看沙箱配置与验收复现入口 →](docs/kubernetes-sandbox.md#构建渲染与后续验收)

<a id="quick-start"></a>

## 🚀 快速开始

以下命令在 **Linux / WSL2 的 Bash** 中运行。准备 **Python 3.12**、[uv](https://docs.astral.sh/uv/)；Web 工作台还需要 **Node.js 22.12+** 构建前端。

### 1. 安装并配置模型

```bash
git clone https://github.com/zed123214/kitagent.git
cd kitagent
uv sync --frozen --extra web
cp .env.example .env
```

编辑 `.env`，填写模型服务配置：

```dotenv
ANTHROPIC_API_KEY=your-api-key
AGENTRT_LLM_DEFAULT_MODEL=claude-sonnet-4-6
```

### 2. 构建工作台

```bash
cd frontend
npm ci
npm run build
cd ..
```

### 3. 启动 Core 与 Web 网关

在项目根目录打开两个终端。

**终端一 · Core**

```bash
uv run --frozen --extra web agentrt-core
```

**终端二 · Web 网关**

```bash
uv run --frozen --extra web agentrt-web
```

打开网关输出的启动链接（`http://localhost:8765/#bootstrap=…`），新建会话，即可提交第一条任务。默认使用 **Loop + Local**，工具在 Core 的工作目录中执行。

### 也可以从终端开始

Core 启动后，在另一个终端使用 CLI 或 TUI：

```bash
# 检查连接
uv run --frozen --extra web agentrt ping

# 提交任务
uv run --frozen --extra web agentrt run --goal "阅读项目结构，整理主要模块及其职责"

# 打开终端交互界面
uv run --frozen --extra web agentrt-tui
```

<details>
<summary><strong>无需 API Key：体验执行引擎与跨进程恢复</strong></summary>

运行模型 → 工具 → 模型的离线示例：

```bash
uv run --frozen --extra graph python examples/graph_offline_demo.py
```

体验 Core 重启后续接任务、复用已完成的工具结果：

```bash
uv run --frozen --extra graph-sqlite python examples/durable_recovery_demo.py
```

浏览器离线演示见[工作台说明](docs/web-workbench.md#无-api-key-的真实工具演示)。

</details>

### 选择运行模式

| 模式 | 适用场景 | 使用指南 |
| --- | --- | --- |
| **Loop + Local** | 浏览器工作台、本地开发与日常任务 | [工作台](docs/web-workbench.md) · [运行手册](RUNBOOK.md) |
| **Graph + Memory** | 显式节点编排与进程内会话续接 | [Graph 引擎](docs/graph-engine.md) |
| **Graph + SQLite + Local** | Core 重启恢复与持久化人工审批 | [恢复配置](docs/durable-recovery.md) |
| **Loop / Graph Memory + Kubernetes** | 按会话分配的容器工作区 | [沙箱部署](docs/kubernetes-sandbox.md) |

<a id="operator-demo"></a>

## 🧪 应用案例：算子开发与性能优化

想把 Agent 用在更复杂的开发任务中？这份案例从 **Equal** 的广播、分块与数据复用，讲到 **SparseFlashAttentionGrad** 的矩阵核与向量核协作、流水排程和负载均衡。

案例按“读懂任务 → 找到瓶颈 → 修改与测试 → 对照验证”组织，附有迭代记录和可复制的任务提示词。在 KitAgent 中，你可以用同一会话推进这些步骤，查看工具输出、处理审批并导出报告。

[阅读全文：用 Agent 做算子优化 →](docs/operator-optimization.md)

<a id="docs"></a>

## 📚 文档导航

| 我想…… | 从这里开始 |
| --- | --- |
| 使用浏览器工作台 | [Web 工作台](docs/web-workbench.md) |
| 配置并运行项目 | [运行手册](RUNBOOK.md) |
| 理解任务执行链路 | [系统架构](docs/architecture.md) · [Agent Loop](docs/agent-loop.md) |
| 使用 Graph 与故障恢复 | [Graph 引擎](docs/graph-engine.md) · [持久化恢复](docs/durable-recovery.md) |
| 部署 Kubernetes 沙箱 | [部署指南与验收复现](docs/kubernetes-sandbox.md) |
| 配置权限和会话记忆 | [工具权限](docs/tool-permissions.md) · [会话记忆](docs/session-memory.md) |
| 学习算子优化工作流 | [Equal 与 SparseFlashAttentionGrad 案例](docs/operator-optimization.md) |
| 扩展工作流程与工具 | [Skills / Subagents / MCP](docs/skills-subagents-mcp.md) |
| 开发客户端或参与贡献 | [通信协议](WIRE_PROTOCOL.md) · [贡献指南](CONTRIBUTING.md) |

## 🤝 参与贡献

欢迎通过 [Issues](https://github.com/zed123214/kitagent/issues) 分享使用场景、反馈问题，或提交 Pull Request。开发环境与检查命令见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 License

[MIT](LICENSE)
