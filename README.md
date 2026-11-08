<div align="center">

<h1>KitAgent</h1>

<p><strong>在浏览器与终端中，运行你的 AI Agent</strong></p>

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

[产品演示](#demo) · [算子开发演示](#operator-demo) · [核心能力](#features) · [系统架构](#architecture) · [快速开始](#quick-start) · [文档导航](#docs)

</div>

---

KitAgent 面向希望构建和使用 AI 自动化工具的开发者。你可以在浏览器或终端中描述任务，让 Agent 阅读项目、执行命令、修改文件，并在同一会话中继续协作。通过工作台，你能查看每次工具调用、处理审批、追踪子任务，并导出本轮运行报告。

项目以常驻 **Core** 管理执行与会话，提供 **Web / CLI / TUI** 三种交互入口，支持 **Loop / LangGraph** 执行引擎，以及 **Local / Kubernetes** 工具环境。

<a id="demo"></a>

## 📸 产品演示

**从一句任务描述，到可查看、可导出的执行结果。**

![KitAgent 46 秒操作演示：提交任务、审批工具调用、查看执行结果与导出报告](docs/assets/web-workbench-demo.gif)

<p align="center">
  会话管理 · 多轮对话 · 工具时间线 · 运行报告<br />
  <a href="docs/assets/web-workbench-overview.png">查看高清截图</a> · <a href="https://raw.githubusercontent.com/zed123214/kitagent/main/docs/assets/web-workbench-demo.webm">下载完整视频</a> · <a href="docs/web-workbench.md">启动工作台</a>
</p>

以仓库检查为例：

> 检查样例 Python 仓库，执行检查脚本并生成检查报告。

| 步骤 | 你在工作台中看到的内容 |
| --- | --- |
| **① 描述目标** | 新建会话，用自然语言提交任务。 |
| **② 观察执行** | 查看 Agent 回复、工具参数、执行状态与输出。 |
| **③ 参与决策** | 在审批卡片中批准或拒绝调用，也可记住本会话的工具授权。 |
| **④ 获取结果** | 查看本轮结论、工具记录与审批记录，导出运行报告后继续对话。 |

<details>
<summary><strong>展开查看：工具调用与人工审批</strong></summary>

![KitAgent 审批界面：查看待执行工具及参数，选择批准或拒绝](docs/assets/web-workbench-approval.png)

工作台提供「只读 / 按需询问 / 自动批准」三种会话权限模式，并支持查看和撤销已记住的工具授权。

</details>

<p align="center"><sub>内置离线演示 · 脚本化模型响应 + 实际工具执行 · <a href="docs/web-workbench.md#无-api-key-的真实工具演示">在本机体验</a></sub></p>

<a id="operator-demo"></a>

### 🧪 场景演示：从 Equal 开发到 SparseFlashAttentionGrad 优化

用两个昇腾 Ascend C 算子展示多轮工程协作：**读懂规格 → 建立正确基线 → 定位瓶颈 → 修改与回归 → 保存交付证据**。Equal 展示完整算子的开发，SparseFlashAttentionGrad 展示复杂梯度算子的性能迭代。

以下流程根据已有项目源码说明与实验归档整理，提示词可用于 KitAgent 工作台演示；历史成绩不代表这次由 KitAgent 重新执行所得。上方 GIF 仍为仓库检查演示。

| 阶段 | Equal：从语义到可交付算子 | SparseFlashAttentionGrad：从基线到性能优化 |
| --- | --- | --- |
| **① 拆解任务** | 明确逐元素相等、BOOL 输出、最多 8 维广播，以及 NaN、正负零、INT64 极值语义。 | 梳理稀疏索引、重复索引计数和 dQ / dK / dV 梯度，列出 RoPE、可选 Value 等分支。 |
| **② 建立基线** | 串起 OpDef、InferShape、Host Tiling、Ascend C Kernel 与 ACLNN 两段式接口；对照 CPU golden。 | 固定源码、输入和参考梯度，先通过精度检查，再记录分阶段耗时与核间等待。 |
| **③ 提出并实施优化** | Host 广播轴压缩与 stride 预计算；连续片段向量比较、多核分块、UB 缓存复用；INT64 拆为高低 32 位精确比较。 | 在满足条件时批量统计重复索引；将就绪汇总交给 AIV，调整 512 行的五分片任务与 dK / dV 归约分配。 |
| **④ 用实验作取舍** | 分开运行 custom / builtin，核验实际加载库，比较精度、设备耗时与验收阈值。 | 保留变慢候选；根据分段记录调整任务归属，用两种执行顺序配对复测。 |
| **⑤ 交付与复盘** | 绑定源码版本、测试矩阵、CSV 和验收说明，形成社区交付材料。 | 分开保存正式提交、历史样机、赛后整理版及报告，记录每项优化的适用范围。 |

<details>
<summary><strong>演示一 · Equal：开发、广播优化与验收</strong></summary>

在工作台中分轮提交，先检查 Agent 给出的实现与证据，再继续下一步：

> **第一轮 · 阅读与规划**<br />
> 阅读工作区中的 Equal 任务书、源码和测试材料。整理输入输出契约、dtype、广播规则与边界情况，说明 Host Tiling、Kernel、ACLNN 的职责，列出实现和验证顺序。

> **第二轮 · 开发与优化**<br />
> 以当前正确版本为基线，检查广播索引和数据搬运开销。选择一项有代码依据的优化，说明预期收益与回退条件，修改后验证同形状、多维广播、尾块及特殊值；保留修改前后的版本。

> **第三轮 · 验收与交付**<br />
> 核对 custom 与 builtin 的加载路径，按相同输入比较精度和设备耗时。报告源码版本、环境、采样方法、逐项结果及失败项；没有 NPU 时只整理复测命令和待验证项。

**历史交付：** Equal 最终源提交 `763a5cf5` 的既有记录为精度 **306/306**、性能阈值 **306/306** 达标；项目材料记录代码经 [cann/ops-math PR #5425](https://gitcode.com/cann/ops-math/pull/5425/discuss) 合入。

性能口径为 5 次预热、10 次设备任务计时取中位数。设内置耗时为 B、自定义耗时为 C：B < 15 μs 时要求 C ≤ B + 3 μs，否则要求 B/C ≥ 0.95。压力套件中 131 条沿用可追溯旧内置基线，另 4 条做两轮双侧配对复测。因此“达标”不等于每条都更快，也不代表 A2 / A3 双硬件均独立跑完这套测试。

</details>

<details>
<summary><strong>演示二 · SparseFlashAttentionGrad：定位瓶颈、失败回退与配对验证</strong></summary>

> **第一轮 · 找到瓶颈**<br />
> 阅读 SparseFlashAttentionGrad 的基线、频数统计实现和 profiling 记录。检查重复索引是否保留重数，区分计算、搬运和就绪等待；每个瓶颈判断都给出对应证据。

> **第二轮 · 迭代方案**<br />
> 分析五分片候选为何变慢，检查短块核承担的 dK / dV 工作。调整任务映射时保持输出归属和完整归约，先验证三梯度，再按正反两种顺序与同条件基线比较；保留失败记录。

> **第三轮 · 整理交付**<br />
> 将正式提交、历史样机和可读整理版分别归档。绑定源码哈希、vendor、输入哈希和测试报告，汇总精度、性能及未验证范围，再从工作台导出本轮报告。

**一次有记录的优化迭代：**

| 决策 | 观察到的结果 | 后续动作 |
| --- | --- | --- |
| 放弃五分片初稿 | 两种顺序的耗时分别增加 **4.76% / 1.47%**；分段记录显示 dK / dV 尾部集中在短块核。 | 重新分配归约任务，保留退化记录。 |
| 晋级调整后的历史组合样机 | 910B3 上，正序 **280.17 → 258.99 μs**，反序 **275.31 → 259.71 μs**，耗时分别下降 **7.56% / 5.67%**。 | 按其自身连续 C1 对照评估，再进入集成；该数据限历史样机两种顺序，未测最终单机制消融。 |
| 核验赛后 R5 整理版 | 910B4 / CANN 8.5.0 下，28 场景 × 两版产生 **56 份 FP16 精度报告、112 次毒值检查**；15 种几何、180 份 Event 计时报告的候选/原版中位数比几何平均为 **0.99555**。 | 通过预设无大回退门槛；BF16 仅有模板编译覆盖。 |

正式提交 `1041451` 在 **2026-10-31** 留档榜单中为 **Pass / 47.21 分**；赛后 R5 的回归结果单独记录。样机优化收益、官方分数与整理版回归属于不同测量口径。

</details>

**在 KitAgent 中演示：** 按[快速开始](#quick-start)启动工作台，将源码和测试材料放到工具可访问的工作区，使用真实模型逐轮提交上述任务；在工具时间线查看读文件、修改、构建与测试输出，按会话权限处理审批，最后导出运行报告。设备测试需要另行准备兼容的昇腾 NPU、驱动、CANN 和测试工具；默认 Local / kind 环境不提供这些硬件能力。

<details>
<summary><strong>材料来源与结果范围</strong></summary>

本节依据 `Equal算子开发流程与面试讲解.md`（2026-09-16，第 3、11、12 章）及 `星辰杯_答辩材料包_2026-11-06` 中的技术解读、优化历程和实验记录整理。SparseFlashAttentionGrad 数值对应 E01 榜单摘录、E02 精度状态、E03 配对比较、E11 样机决策及五分片初稿记录；原始材料未随 KitAgent 仓库分发。

这里展示可采用的工程协作流程与历史案例。已有材料披露 AI 参与代码研究、修改、实验编排及证据整理，未提供可归因于 KitAgent 的端到端运行记录或人工工时对照；不据此量化 Agent 效率收益。

</details>

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
| 扩展工作流程与工具 | [Skills / Subagents / MCP](docs/skills-subagents-mcp.md) |
| 开发客户端或参与贡献 | [通信协议](WIRE_PROTOCOL.md) · [贡献指南](CONTRIBUTING.md) |

## 🤝 参与贡献

欢迎通过 [Issues](https://github.com/zed123214/kitagent/issues) 分享使用场景、反馈问题，或提交 Pull Request。开发环境与检查命令见 [CONTRIBUTING.md](CONTRIBUTING.md)。

如果 KitAgent 对你有帮助，欢迎点一个 **Star**，也欢迎分享你用它完成的任务。

## 📄 License

[MIT](LICENSE)
