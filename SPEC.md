# hermes-redteam SPEC

> 历史设计稿（P0/P1）。部分假设已过时：default 已启用、插件已 GitHub 安装、授权由靶标名隐含（不再要求五字段表）、preflight 不再注册为技能。当前实现以 README / docs/USAGE.md 和代码为准。

状态：草案，2026-10-16。尚未写插件代码。与本文件冲突的实现视为错误。

## 目标

把 `youzaiooo/Hermes-dsh-redteam-mode` 的编排与事实记录，重做成 Hermes 插件 `hermes-redteam`。不嵌入 DSH，不修改 Hermes 核心，不改 Sekhmet 人格。

只服务已授权的演练 / 渗透测试。插件不包含 exploit、payload、WebShell 管理器，也不自动下载它们。

## 已冻结决策

1. 事实层是每靶标一个本地作战 Wiki，加一个结构化索引。索引用嵌入式 SQLite，不用 PostgreSQL，也不写共享 Wiki。
2. 得分规则保留，默认 `off`。三档 `off | visible | enforced` 做进桌面插件 UI。
3. 五个永久执行 profile：`rt-recon`、`rt-asset`、`rt-vuln`、`rt-exploit`、`rt-internal`。用户只和 Sekhmet 说话。Sekhmet 兼任指挥、授权审查、方案审查和报告审查。不另设 `rt-lead`。
4. Sekhmet 的 default profile 不 enable 整套插件，避免执行工具进入每次评估会话。指挥纪律在 `~/.hermes/skills/redteam-commander/SKILL.md`，只在谈靶标时用 `skill_view` 加载。派工走 `hermes kanban`，不把执行工具注册进 default。
5. 演练事实只进该靶标的 Wiki 和 `index.db`。长期记忆只收跨靶标、可复用、已脱敏的经验。开发以本文件为规格源。

## 1. 事实层

### 为什么不是 PostgreSQL

本机已安装 `postgresql 18` 与 `psycopg 3.3.4`，但服务是 `inactive`，没有监听 5432。能装，不是不能用。

不用它，因为这份数据的生命周期是「一个演练靶标一份档案」：

- 演练结束应能整目录丢弃。SQLite 是 `$HERMES_HOME/redteam/engagements/<id>/index.db` 一个文件。PostgreSQL 是集群、角色、库、备份策略。
- 五个执行 profile 是五个 OS 进程。PostgreSQL 当然能并发写，但要多一个始终在线的服务、认证和迁移。插件不应依赖「数据库已经起来」。
- 资产、端口、漏洞状态是索引和约束，不是分析型查询。不需要服务端、复制、远程客户端。
- 共享一个 PostgreSQL 会把所有靶标的凭据索引放进同一个长期服务。单文件库跟着靶标走，丢弃边界更清楚。

PostgreSQL 只在以后出现这些需求时再换：多机同时写同一靶标、要远程 SQL 客户端、或索引大到 SQLite 锁等待不可接受。换存储时 Wiki 路径和工具 JSON 契约不变，只换 `store.py`。

### 布局

```
$HERMES_HOME/redteam/engagements/<id>/
├── index.db          # 结构化索引，唯一机器写入口
├── wiki/             # 本地作战 Wiki，给人读，也给 agent 开工时读
│   ├── SCHEMA.md
│   ├── index.md
│   ├── log.md
│   └── pages/
└── raw/              # 报文、截图、命令输出。库里只留路径和 sha256
```

共享 Wiki `~/wiki` 禁止写入。禁止内容：凭据真值、Cookie、私钥、私网段清单、逐单位战果统计。

### 索引里有什么

资产、端口、服务、指纹、测试状态、漏洞结论指针、凭据指针、会话/隧道指针、证据路径、攻击链步骤指针、得分规则开关状态。

原文、截图、HTTP 报文不进库，也不进模型上下文。工具返回路径、哈希、一行结论。

并发写只走工具。Wiki 页面由工具生成骨架，agent 补叙述。两个角色不许同时手改同一页。

### 记忆里只放经验

靶标事实不进 Mnemosyne，也不进 `MEMORY.md`。单位名、资产、端口、漏洞、凭据、隧道、战果都只活在该靶标目录里。下次演练目标不同，这些记录没有长期召回价值，还有串靶标的风险。

工具和角色技能禁止把上述事实写入记忆。开工先读该靶标 `wiki/index.md`，不靠记忆召回。

可以进长期记忆的，必须同时满足：不含目标标识、换一个靶标仍然成立、经过用户确认。例如「某类面板的默认入口路径已改，旧指纹会漏报」「FOFA 查询要排除 CDN 段，否则资产清单被污染」。写法是方法，不是战例。

经验页也可以写在插件自己的本地笔记里，仍不得进入共享 netsec Wiki。默认不自动写入。

`rt-*` 和 Sekhmet 都不把演练事实写进记忆。Sekhmet 当前 `profile_isolation: false`、`default_scope: global`，指挥会话比执行角色更容易把单位名写进去。工具禁令盖不住对话中直接调用记忆工具，所以 `redteam-commander` 禁止调用 `mnemosyne_remember`、`mnemosyne_shared_remember` 和 `memory` 记录靶标事实。现在不改 default 的记忆配置。`rt-*` 也不必为了防泄漏而关掉共享记忆：它们本来就不该把演练事实写进去。

### 授权记录是靶标的第一页

`redteam_engagement_open` 必须先写出 `wiki/authorization.md`：授权方、范围、时间窗、允许的手段、联系人。字段可以先空着，但文件必须在。空授权时，预检返回 `blocked`，资产写入以外的主动动作工具一律拒绝。授权书本身不进记忆，也不进共享 Wiki。

## 2. 得分规则

规则表保留在插件内，默认不驱动行为。

`plugins.entries.hermes-redteam.score_rules`: `off | visible | enforced`

| 档 | 工具 | 面板 | 角色提示词 |
|---|---|---|---|
| off | 不注册得分工具 | 显示开关，内容区隐藏 | 不提得分 |
| visible | 只读展示 | 显示规则与命中，不计分 | 不要求先对齐得分点 |
| enforced | 允许记录命中，服务端判定上限 | 显示并允许操作 | 恢复「先问落到哪个得分点」 |

桌面插件必须有这个开关，不能只改配置文件。开关写 `config.yaml`，不写 `.env`。进行中的会话不热改工具集，避免拆 prompt cache。下一轮会话生效。UI 要标明「已保存，新会话生效」。

默认 `off`。

## 3. Profile

| Profile | 职责 | 工具面 |
|---|---|---|
| rt-recon | 被动/主动信息收集，域名、子域、端口、指纹 | 预检、资产写入、资产查询 |
| rt-asset | 资产梳理、去重、优先级、测试状态 | 资产查询、关联、状态更新 |
| rt-vuln | 漏洞检测与证据指针 | 资产查询、漏洞写入、证据路径 |
| rt-exploit | 已授权验证、访问与凭据指针 | 漏洞查询、凭据指针、访问指针 |
| rt-internal | 已授权内网后续，隧道与横向状态 | 会话/隧道指针、资产写入 |
| default（Sekhmet） | 唯一用户入口。指挥、审授权、审方案、审报告 | 不注册执行工具。`skill_view` 加载 `redteam-commander` |

五个执行 profile 是永久身份：各自的 SOUL、记忆、技能、模型配置。它们不是插件内部子进程。插件只提供工具，Hermes 提供 profile。

用户只和 Sekhmet 说话。Sekhmet 拆卡、用 `hermes kanban create` 和 `hermes kanban assign` 派给执行 profile、核对 Wiki 是否落库、向用户汇报。执行角色不互相派活，也不向用户直接开新战线。每个执行 profile 可以再派一层子代理，`delegation.max_spawn_depth` 保持 1。

同靶标执行中的工人软上限是 3。P0 不执行这条。P1 起，写入工具先占 `reservation`，超出则拒绝写入。这只是工具层约束，不改 Hermes 运行时上限。

高风险动作由 Sekhmet 停下来问用户。Sekhmet 不代为执行扫描，也不用 `delegate_task` 把执行角色拉成自己的临时子代理。临时子代理没有独立记忆，也不能再派下一层。

### 为什么不在 default enable 整套插件

兼任指挥不等于把插件 enable 在 Sekhmet 上。

- enable 后，技能进入该 profile 的 `skills_list` 和系统提示词。执行工具会进每一次安全评估会话。
- 两个进程不能写同一个 profile 的记忆。执行工人必须是独立 profile。
### 面板挂载未决

桌面后端 `plugin_api.py` 只在该 gateway profile 的 `plugins.enabled` 里挂载。本机桌面连的是 default。面板若要出现在 Sekhmet 的窗口里，P2 必须先实测：只挂只读查询路由和得分开关，不调用 `register_tool()`、不调用 `register_skill()`。

测不通就不 enable。面板改放到某个执行 profile 的桌面会话，Sekhmet 用 Wiki 文件核对。得分开关这时不在 Sekhmet 窗口里，改用 `hermes config set`。这条在实测前不是已定方案。

### 技能按加载位置分开

插件一旦在执行 profile 上 enable，`register_skill()` 注册的技能会进入该 profile 的系统提示词。不能把 23 个技能一次全注册，否则 `rt-recon` 也会看到利用类技能。P1 只注册两个：`redteam-preflight`，以及按当前 profile 名选择的一份 `roles/<profile>.md`。其余角色文件留在包内，不进技能列表。

`redteam-commander` 已在 `~/.hermes/skills/redteam-commander/SKILL.md`。它不通过插件 `register_skill()` 注册。`register_skill()` 会把技能放进该 profile 的系统提示词；放在个人 skills 目录，才只在 `skill_view` 时加载。当前会话的技能索引在会话开始时缓存，本会话看不到它，下一会话才出现在 `skills_list`。P0 不建 Kanban 卡。

当前机器只有 `default` profile。五个执行 profile 在 P3 才创建，不在 P0 创建。

## 4. 插件形状

```
~/.hermes/plugins/hermes-redteam/
├── plugin.yaml
├── __init__.py
├── store.py
├── schema.sql
├── score_rules.py
├── tools_registry.py
├── preflight.py
├── skills/<name>/SKILL.md
├── roles/*.md
├── dashboard/manifest.json
├── dashboard/plugin_api.py
└── desktop/plugin.js
```

源码仓库是 `~/src/hermes-redteam`。安装用 `hermes plugins install` 链到 `~/.hermes/plugins/`，不写进 Hermes 核心仓库。

数据目录是 `$HERMES_HOME/redteam/`，不是 `~/.dsh/redteam/`。

## 5. 不做

- 不自动 `sudo apt`，不自动下载 fscan、冰蝎、哥斯拉、suo5、chisel、frp。
- 不把 exploit 步骤、payload、凭据真值写入插件仓库、共享 Wiki、SESSION.md。
- 不把靶标事实写入 Mnemosyne 或 `MEMORY.md`。记忆只收已确认的脱敏经验。
- 不替换 Hermes 内置工具，不申请 `tools.override`。
- 不把红队模式写进 Sekhmet 的 SOUL。指挥纪律在 `~/.hermes/skills/redteam-commander/SKILL.md`。
- 不在 P0 注册漏洞利用类工具，不创建 profile。
- 不绕过 Hermes 的命令审批。插件不提供「自动批准扫描」的开关。

## 6. 阶段

| 阶段 | 交付 | 验收 |
|---|---|---|
| P0 | `index.db` + 本地 Wiki 骨架；打开/绑定靶标；资产写入与查询；preflight 只读 | 单元测试不访问外网，不启动 PostgreSQL |
| P1 | 按角色注册落库工具；`/redteam`；得分开关的配置读写；`reservation` 软上限 3 | 未 bind 的会话看不到写入工具；第 4 个并发写入被拒绝 |
| P2 | 桌面 pane。先实测只读路由能否不注册工具和技能 | 测通才挂到 default；测不通则面板不进 Sekhmet 窗口 |
| P3 | 创建五个执行 profile 与 Kanban 交活说明 | profile list 能看到五个 `rt-*`；default 仍未 enable 整套插件；Sekhmet 能用 kanban CLI 派一张测试卡 |

P0 完成前不开始 P1。
