# KitAgent 更新日志

## Unreleased

以下变更于 2026-11-18 至 2026-11-20 合入 `main`。

### 新增功能

- Core 新增 OpenAI Chat Completions Provider，支持流式响应、按索引组装并行工具调用，以及对话历史压缩。维护者 @zed123214，[#23]。

### Bug 修复

- `agentrt run` 在 Core 接受任务后提前断连时给出诊断并以退出码 `1` 结束；若已收到 `run.finished`，则按任务结果返回退出码。社区贡献者 @zoutianjun，[#17]。
- `agentrt trace --follow` 读完历史记录后沿用同一文件游标，切换到实时跟踪时追加的完整 JSONL 记录会按顺序输出一次。社区贡献者 @zoutianjun，[#20]。
- 会话将单独的 `/` 或其后只有空白的输入原样作为普通消息处理，修复了查找空技能名时抛出的 `IndexError`。社区贡献者 @zoutianjun，[#21]。

### 安全性

- Bash 审批现在也检查引号内以及选项或赋值中的路径。命中工作目录外路径规则时，即使会话已记住 Bash 授权，仍需审批。无法解析 shell 参数时也请求审批，显式拒绝规则优先。维护者 @zed123214，[#24]。

### 兼容性

- Core 默认使用 Anthropic。切换到 OpenAI 时，在服务端设置 `AGENTRT_LLM_PROVIDER=openai` 和 `OPENAI_API_KEY`；已有显式模型配置时，将 `AGENTRT_LLM_DEFAULT_MODEL` 改为目标端点可用的模型。重启 Core 后，CLI 和 Web 共用该配置。[#23]
- 具名技能调用（如 `/skill-name`）继续按原有流程解析。[#21]

### PR 验证记录

下表引用各 PR 作者报告的结果。每行对应各自的测试范围，本次整理未重跑测试。

| PR | 执行环境 | 验证范围与结果 |
| --- | --- | --- |
| [#17] | 定向测试未单列环境；另有 macOS / Python 3.12 离线回归 | CLI 与 SocketClient 共 12 项通过，覆盖终态事件与断连的先后顺序。另一次离线回归中，3 项沙箱测试触及 Unix 套接字路径长度限制，缩短临时目录路径后重跑通过。 |
| [#20] | PR 未注明操作系统或 Python 版本 | CLI trace 与 TraceWriter 共 6 项通过，含首次读到文件末尾后追加记录的回归用例。 |
| [#21] | PR 未注明操作系统或 Python 版本 | 会话管理、技能加载、会话存储与 Web 会话运行共 31 项通过，含两种空技能名输入。 |
| [#23] | WSL，本地模拟 OpenAI 响应 | Provider、Core 与依赖回归共 47 项通过，含 Loop 和 Graph 工具调用往返。测试时缺少真实 OpenAI 凭据，尚无真实 API 验收记录。 |
| [#24] | WSL | 权限策略、权限管理器与会话权限共 52 项通过，覆盖引号路径、选项值、已记住的授权及含空格的相对路径。 |

[#17]: https://github.com/zed123214/kitagent/pull/17
[#20]: https://github.com/zed123214/kitagent/pull/20
[#21]: https://github.com/zed123214/kitagent/pull/21
[#23]: https://github.com/zed123214/kitagent/pull/23
[#24]: https://github.com/zed123214/kitagent/pull/24
