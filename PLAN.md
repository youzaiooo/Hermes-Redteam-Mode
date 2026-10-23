# PLAN

> 历史计划（P0–P3 阶段）。当前状态见 AGENTS.md / README；授权已改为靶标即授权，插件已 GitHub 安装并启用。

当前阶段：P0–P3 骨架完成。工具、表、技能目录、页签清单已对齐。技能正文和窗口挂载未完成。default 未 enable。

## P0 — 索引与 Wiki 骨架

- `schema.sql`：资产、端口、测试状态、证据指针。不含凭据真值列。
- `store.py`：打开靶标目录，初始化 `index.db` 与 `wiki/`。
- 工具仅四个：`redteam_engagement_open`、`redteam_session_bind`、`redteam_asset_add`、`redteam_asset_query`。
- `redteam_preflight`：只报告缺什么，不安装。
- 测试：临时目录，不碰 `$HERMES_HOME`，不连数据库服务。

完成标准：`pytest` 通过，并把结果写进 `SESSION.md`。

## P1 — 落库工具与得分开关

- 漏洞、证据路径、攻击链、报告骨架。
- 得分工具仅在 `score_rules != off` 时注册。
- `check_fn` 按 profile 名裁剪。五个 `rt-*` 只有自己的写入工具。default 不注册执行工具。
- `reservation` 在 P1 生效。同一靶标已有 3 条未释放占用时，写入工具拒绝。P0 不建这张表的写入路径。

## P2 — 桌面 UI

- 先实测：插件 enable 后能否只挂 `plugin_api.py` 的只读路由和得分开关，不调用 `register_tool()`、不调用 `register_skill()`。
- 测通：右侧 pane 挂在 Sekhmet 窗口，页签跟着当前靶标。得分三档开关写配置，提示新会话生效。
- 测不通：不在 default enable。面板改放执行 profile 的桌面会话。Sekhmet 用 Wiki 核对，得分开关用 `hermes config set`。
- `ctx.rest` 轮询，不依赖 `ctx.socket`。

## P3 — Profile 与 Kanban

- 创建 `rt-recon`、`rt-asset`、`rt-vuln`、`rt-exploit`、`rt-internal`。不创建 `rt-lead`。
- 只在这五个 profile enable 整套插件。Sekhmet 用 `skill_view` 加载 `redteam-commander`，再用 `hermes kanban` 指挥。
- 写 Kanban 交活约定，不在本文件里写攻击步骤。
