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

### 🧪 场景演示：用 Agent 协作开发与优化昇腾算子

**从一个正确的算子，到一个能解释、能验证、能交付的优化。** Equal 展示从输入语义到社区验收的开发过程；SparseFlashAttentionGrad 展示算法选型、Cube / Vector 协作、瓶颈定位与失败回退。

以下是可在 KitAgent 中采用的协作流程，结合已有项目记录和算子竞赛现场分享整理。历史成绩来自原项目归档；尚无这两个算子的 KitAgent 端到端实跑记录。上方 GIF 展示的仍是仓库检查任务。

**演示主线：** 接入规格与环境 → 画清计算与数据流 → 实现正确基线 → 比较优化候选 → 测量与回归 → 冻结交付。编译或数值失败时先诊断；精度通过后，再用性能证据决定是否保留优化。

| 阶段 | Agent 要回答的问题 | 本轮应留下的产物 |
| --- | --- | --- |
| **① 接入** | 接口、dtype、shape、硬件与 CANN 版本是什么？怎样判断正确和达标？ | 输入契约、环境清单、基线源码版本与可执行验证命令。 |
| **② 设计** | 计算依赖和数据流是什么？哪些工作交给 Host、AIC（矩阵核）或 AIV（向量核）？ | 计算步骤、数据搬运路径、任务归属及算法候选表。 |
| **③ 实现** | 最小正确路径能否构建、调用并通过参考输出检查？ | 可运行基线、边界测试、首个失败的定位记录。 |
| **④ 优化** | 代价来自索引、计算、搬运、同步还是负载不均？ | 一个可检验的假设、改动差异、适用条件及回退路径。 |
| **⑤ 取舍** | 同输入、同环境下是否更快？扩展场景是否退化？ | 精度矩阵、正反顺序配对计时、分段证据与保留/回退结论。 |
| **⑥ 交付** | 集成后是否仍成立？别人如何复核？ | 冻结源码、构建与加载身份、输入哈希、原始报告及未验证项。 |

<details>
<summary><strong>演示一 · Equal：把语义、实现与验收串起来</strong></summary>

**先把问题讲清楚。** Equal 比较两个可广播 Tensor 的对应元素并输出 BOOL。例如 `[2,1]` 与 `[1,3]` 广播为 `[2,3]`；这要求按输出坐标映射两个输入，不能简单地按相同地址比较。

**再解释实现选择。** Host 压缩广播轴、预计算有效 stride 并制定多核切分；Kernel 按连续片段搬运和比较，复用适用广播模式的 UB 缓存；ACLNN 负责接口校验及必要的输入输出适配。INT64 使用高低 32 位精确比较，避免有损转换。

在工作台逐轮提交，检查产物后再继续：

> **第一轮 · 契约与基线**<br />
> 阅读工作区中的 Equal 任务书、源码和测试材料，列出入口及版本。整理 dtype、最多 8 维广播和输出契约；用一个双侧广播例子解释地址映射。列出 NaN、正负零、INT64 极值、尾块等测试，以及 Host Tiling、Kernel、ACLNN 的职责。先确认构建和正确性基线。

> **第二轮 · 一项优化与反例**<br />
> 从当前正确版本中选择一个仍有证据支持的瓶颈，解释已有广播轴压缩、连续片段和缓存策略的作用。提出一项改动、适用条件和可能变慢的输入；保留基线及回退路径，修改后验证受影响的语义与边界。区分源码推断和设备测量。

> **第三轮 · 配对验收与交付**<br />
> 核对 custom / builtin 的实际加载库与任务类型，按相同输入配对比较。分别记录 Kernel 设备耗时和需要时测量的完整接口耗时。报告版本、环境、预热、采样、阈值与失败项；没有 NPU 时输出复测命令和待验证项。冻结通过验收的版本并导出运行报告。

**历史交付：** Equal 最终源提交 `763a5cf5` 的既有记录为精度 **306/306**、性能阈值 **306/306** 达标；项目材料记录代码经 [cann/ops-math PR #5425](https://gitcode.com/cann/ops-math/pull/5425/discuss) 合入。

性能口径为 5 次预热、10 次设备任务计时取中位数。设内置耗时为 B、自定义耗时为 C：B < 15 μs 时要求 C ≤ B + 3 μs，否则要求 B/C ≥ 0.95。压力套件中 131 条沿用可追溯旧内置基线，另 4 条做两轮双侧配对复测。因此“达标”不等于每条都更快，也不代表 A2 / A3 双硬件均独立跑完这套测试。

</details>

<details>
<summary><strong>演示二 · SparseFlashAttentionGrad：从计算依赖到有证据的优化</strong></summary>

**先保留数学语义，再选择更合适的计算组织。** 输入稀疏索引可能重复：`[2,0,2,3]` 对 key `[0,1,2,3]` 的频数为 `[1,0,2,1]`。重复项对梯度的贡献必须保留，不能仅做去重。

以无 RoPE 且有独立 Value 的主干说明依赖。令 `α` 为缩放系数，`m/z` 为前向对应的稳定化最大值/归一化和，`count` 为有效索引的频数；按唯一 key 聚合后：

```text
score = Q @ Kᵀ                    dP = dOut @ Vᵀ
P = exp(α · score - m) / z         delta = rowsum(dOut · Out)
W = count · P                     G = W · (dP - delta)
dQ = α · G @ K                    dK = α · Gᵀ @ Q
dV = Wᵀ @ dOut
```

这是说明依赖的公式，实际实现按块计算。RoPE、可选 Value、无效索引及长度边界仍需按任务契约处理。AIC 承担矩阵乘，AIV 承担频数、系数与归约等向量工作；具体缓冲位置、搬运、发布与等待关系必须对应所选版本源码。

**将优化变成可验证的问题：**

| 优化问题 | 候选与取舍 | 需要的证据 |
| --- | --- | --- |
| 重复索引如何统计？ | 比较逐条计数与排序后累计边界差；直接二分、分片二分、归并可列为待评估候选，按索引长度、key 范围、重复率和 UB 预算选型。 | 频数一致性、完整梯度精度、排序/查找/合并的总开销。候选名称不代表本项目已实现或更快。 |
| 为什么矩阵核在等？ | 将计算、搬运、就绪发布和等待分开；检查协调工作是否与旧轮 dK / dV 计算争用同一核。 | 设备时间标记或 profiling 的核/阶段时间线，并说明时钟、同步与插桩开销；API 包络不直接等于硬件忙时。 |
| 五分片是否均衡？ | 对 512 行按 128/128/128/64/64 切分时，同时检查 dQ 与 dK / dV 的归属，不能只看行数。 | 每核任务量、末尾关键路径、输出归属、完整归约及同条件配对计时。 |
| 优化是否只对少数输入有效？ | 按 dtype、模式、RoPE、Value、shape、尾块及索引分布构建测试矩阵；优化分支保留明确准入与回退。 | 分列官方公开用例、自建扩展用例和未验证范围；编译通过与设备数值通过分别记录。 |

**建议的四轮提示词：**

> **第一轮 · 计算图与算法候选**<br />
> 阅读基线、任务契约和 golden，画清前向保存量到 dQ/dK/dV 的依赖，解释重复索引的贡献。列出当前频数算法、两个可比较候选及适用条件；标记已实现与待实验内容。先建立正确性基线和测试矩阵，不凭 case 编号决定算法。

> **第二轮 · 测量与瓶颈假设**<br />
> 读取 profiling 或打点记录，按 AIC/AIV 与计算、搬运、发布、等待整理时间线。区分完整调用耗时、Kernel 时间和插桩包络，找出影响完成时间的关键路径。每项结论标注实测、源码推断或待验证，并说明如何控制插桩影响。

> **第三轮 · 修改与反证**<br />
> 解释五分片初稿退化的原因证据，检查短块核的 dK/dV 工作。选择一项假设修改映射，保持输出归属和完整归约；验证所有实际存在的梯度及相关分支。用 baseline→candidate 与 candidate→baseline 两种顺序重复采样；保留变慢结果，多项改动合并时不要声称已证明单项收益。

> **第四轮 · 集成与冻结**<br />
> 按正确性、预期收益、验证成本和回归风险安排剩余工作，预留整包验收时间。冻结候选后统一接口、Host 路由与 fallback，再做集成回归。将正式提交、历史样机和整理版分开，绑定源码哈希、vendor、输入哈希和报告，列出未验证范围。

**一次有记录的优化迭代：**

| 决策 | 观察到的结果 | 后续动作 |
| --- | --- | --- |
| 放弃五分片初稿 | 两种顺序的耗时分别增加 **4.76% / 1.47%**；分段记录显示 dK / dV 尾部集中在短块核。 | 重新分配归约任务，保留退化记录。 |
| 晋级调整后的历史组合样机 | 910B3 上，正序 **280.17 → 258.99 μs**，反序 **275.31 → 259.71 μs**，耗时分别下降 **7.56% / 5.67%**。 | 按其自身连续 C1 对照评估，再进入集成；该数据限历史样机两种顺序，未测最终单机制消融。 |
| 核验赛后 R5 整理版 | 910B4 / CANN 8.5.0 下，28 场景 × 两版产生 **56 份 FP16 精度报告、112 次毒值检查**；15 种几何、180 份 Event 计时报告的候选/原版中位数比几何平均为 **0.99555**。 | 通过预设无大回退门槛；BF16 仅有模板编译覆盖。 |

正式提交 `1041451` 在 **2026-10-31** 留档榜单中为 **Pass / 47.21 分**；赛后 R5 的回归结果单独记录。样机优化收益、官方分数与整理版回归属于不同测量口径。

</details>

<details>
<summary><strong>协作演示 · 主控统一契约，子任务提交可复核候选</strong></summary>

借鉴现场分享中的主控与 worker 分工，可将独立研究交给 [Subagents](docs/skills-subagents-mcp.md)，由主任务负责接口、验收和集成。下面是工作组织建议，并非 KitAgent 自动隔离 Git 仓库或自动合并候选的功能。

| 角色 | 负责内容 | 交回主任务的内容 |
| --- | --- | --- |
| 主控 | 固定基线、公共接口、测试标准与时间预算；安排设备测量，决定取舍。 | 候选清单、集成版本及验收结论。 |
| 算法子任务 | 研究广播映射或频数统计，对比适用条件和成本。 | 源码依据、候选差异、反例与回退条件。 |
| 流水线子任务 | 研究搬运、同步与核间任务分配。 | 时间线证据、关键路径假设及验证方案。 |
| 验证子任务 | 扩展测试矩阵、核验加载身份、整理配对报告。 | 逐项结果、失败记录、版本和输入绑定。 |

若需要并行修改，先为各候选显式准备独立 checkout 或 Git worktree，并在任务中指定路径、允许修改的文件和交付格式。同一会话的子 Agent 默认共用工具工作区；同一 NPU 上的对比测量应串行安排，避免候选互相干扰。

> **可复制的主控提示词**<br />
> 先固定输入契约、基线提交、验证命令与验收门槛。将算法分析、流水线分析、测试矩阵整理拆成独立子任务，先只读研究；需要写入时为候选准备独立目录。每个候选交回改动、适用条件、精度/性能证据及失败项，由主任务统一集成、全量回归并冻结交付。

</details>

**在 KitAgent 中演示：** 按[快速开始](#quick-start)启动工作台。先提供工具可访问的源码、规格、golden 和历史报告路径，说明可用硬件；再使用真实模型逐轮提交任务，查看工具调用、处理会话审批并导出报告。设备测试需另备兼容的昇腾 NPU、驱动、CANN 和测试工具；默认 Local / kind 环境不提供这些硬件能力。

**没有 NPU 时也能演示：** 完成契约梳理、源码解释、候选比较和对已有报告的离线复核，交付测试矩阵与复测命令；设备精度、性能和同步行为保持“待验证”。原始项目材料未随 KitAgent 分发，使用这些案例前需自行准备。

<details>
<summary><strong>材料来源、方法参考与结果范围</strong></summary>

历史结果依据 `Equal算子开发流程与面试讲解.md`（2026-09-16，第 3、11、12 章）及 `星辰杯_答辩材料包_2026-11-06`。SparseFlashAttentionGrad 数值对应 E01 榜单摘录、E02 精度状态、E03 配对比较、E11 样机决策及五分片初稿记录；原始材料未随仓库分发。

方法参考来自算子竞赛现场分享照片中的“选择合适算法”“用打点绘制流水线图”“技术方案：计算流程”“开发方法：Agentic Ops Develop”“问题重述”“数据集划分”及“比赛策略：按收益分配时间与额度”等内容；部分画面受遮挡，仅采用可辨识的方法思路。照片和他人的实验数据未收录为本项目成果。

本文将上述方法重新组织为 KitAgent 协作示例。现场展示的 `asc-setup / asc-design / asc-implement / asc-optimize / asc-profile / asc-loop / asc-debug / asc-submit` 属于外部 `asc-op-dev` 示例，KitAgent 未内置这些命令。算法候选和扩展测试矩阵属于建议工作，不能视为已有实现或测试覆盖。

已有项目材料披露 AI 参与代码研究、修改、实验编排及证据整理，未提供可归因于 KitAgent 的端到端运行记录或人工工时对照；不据此量化 Agent 效率收益。新增方法说明不改变上述历史成绩的测量范围。

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
