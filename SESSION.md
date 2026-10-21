# SESSION

更新：2026-10-16

阶段：P0–P3 骨架完成。DSH 全流程未完成。五个 profile 已建。插件只在执行 profile enable。default 未 enable。

已决定：

- 索引用每靶标 SQLite 文件，不用 PostgreSQL。
- 作战 Wiki 在 `$HERMES_HOME/redteam/engagements/<id>/wiki/`。
- 得分规则默认 off，UI 三档开关，新会话生效。
- Profile：rt-recon、rt-asset、rt-vuln、rt-exploit、rt-internal。P3 才创建。不设 rt-lead。
- 用户只和 Sekhmet 说话。Sekhmet 兼任指挥、审授权、审方案、审报告。
- default 不 enable 整套插件。指挥 skill 在 `~/.hermes/skills/redteam-commander/SKILL.md`，谈靶标时用 `skill_view` 加载。派工走 `hermes kanban create` 和 `hermes kanban assign`。
- 演练事实只进靶标 Wiki 和 index.db。记忆只收跨靶标、已脱敏、用户确认过的经验。
- 技能按 profile 注册一份角色文件，不全量注册。
- 开靶标先写 `wiki/authorization.md`。授权为空则预检 blocked。
- reservation 表从 P1 开始用。P0 不执行软上限 3。

本轮改动：创建五个空 profile，只复制模型配置和一条模型密钥。没有复制 SOUL、MEMORY、USER。插件源码链接到五个 profile 的插件目录并 enable。default 的 config 不含 hermes-redteam。Kanban 测试卡 `t_b5c14205` 指派给 `rt-recon`，状态 blocked。

验收：2026-10-16T06:59:00Z。`pytest tests -q` 为 27 passed、1 skipped。`hermes profile list` 能看到五个 `rt-*`。`hermes kanban show t_b5c14205` 能看到唯一 assignee。

本地验证：127.0.0.1:8765 静态靶场返回 `lab range ok`。插件打开 `lab-range`，写入资产指针 `range-web`。授权页存在但为空，预检返回 `blocked`。靶场进程已停。全套测试 2026-10-16T07:04:21Z 为 27 passed、1 skipped。

未决：DSH 全流程未完成。本轮已修角色裁剪和未 bind 会话拒绝写入。已补 `vuln`、`http_evidence`、`credential_ref` 三张表，并给 `rt-vuln` 注册 `redteam_vuln_add`、`redteam_http_evidence_add`。现有 12 个工具、9 张表，对照原项目 56 个工具、23 个技能、9 个页签、22 张表。P2 面板仍未挂进 Sekhmet 窗口。

验收：2026-10-16T18:10:59Z。`pytest tests -q` 为 99 passed、1 skipped。本轮按角色注册技能：`rt-recon` 拿到信息收集技能，拿不到利用和内网技能。

本地闭环：2026-10-16。`nginx:alpine` 只绑 `127.0.0.1:8765`。`lab-local` 授权、预检、占位、资产、扫描路径、报告索引均通过。`scan_ref` 只存 `raw/scans/range-web.txt`。报告索引不含 `nmap` 或 `payload`。靶场容器已停。

面板数据：2026-10-17。桌面半边先读 `/engagements/current`，再按靶标 id 拉各页。总览用 `asset_count` / `finding_count`，漏洞页读 `vulns`。`plugin_api.py` 改为按文件路径加载 `score.py` / `store.py`，单独 import 不再因相对导入失败。得分开关仍会改 `config.yaml`，默认 off。
