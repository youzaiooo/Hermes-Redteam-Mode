# hermes-redteam

把 Hermes Agent 变成一台**已授权**的红队作战指挥台：一个靶标名称 → 指挥会话开靶标 → 按阶段把任务派给五个常驻执行 profile → 资产/漏洞/凭据/隧道/得分全部落进每靶标独立的 SQLite 事实库 → 右侧中文控制台实时可视化。

> 仅限已获授权的攻防演练 / 渗透测试。仓库不包含 exploit、payload 或凭据真值；事实只落本机 `$HERMES_HOME/redteam/engagements/<id>/`。

## 和原项目的区别

原项目 [dsh-redteam-mode](https://github.com/Jueze-2019/dsh-redteam-mode) 在 DSH 里**临时拉起子智能体**；本项目按用户的设计改为：

- **五个常驻 profile**：`rt-recon` / `rt-asset` / `rt-vuln` / `rt-exploit` / `rt-internal`。每个有自己的模型、技能、记忆与工具面，技能上限更高，可以独立升级。
- **Sekhmet（default）只做指挥**：只拿读取/查询/派工工具，不拿执行工具，保持精简。
- **派工走 Hermes kanban**：`redteam_dispatch` 建卡 → 网关 dispatcher 拉起对应 profile → worker 干完活把结果落到靶标库 → 指挥用 `redteam_dispatch_status` 跟进。

## 结构

```
plugin.yaml           # 插件清单（指挥官工具面）
__init__.py           # register(ctx)：按 profile 分发工具与技能
dispatch.py           # redteam_dispatch / dispatch_status（kanban 派工）
store.py              # 每靶标 SQLite：资产/漏洞/证据/凭据/隧道/攻击链/得分
tools.py              # 工具 schema + handler
preflight.py          # 工具/授权预检
roles/                # 五个执行角色提示词
skills/               # 指挥 + 25 个实战技能（从 DSH 原项目移植）
dashboard/
  plugin_api.py       # /api/plugins/hermes-redteam/* 只读数据
desktop/plugin.js     # 中文桌面面板（态势/资产/成果/报告/资源）
tests/
```

## 安装

### 方式 A：一条命令（推荐）

```bash
hermes plugins install youzaiooo/Hermes-Redteam-Mode --enable
bash ~/.hermes/plugins/hermes-redteam/scripts/install.sh
```

`install.sh` 做三件事：给 `default` 和五个 `rt-*` profile 启用插件与 `hermes-redteam` 工具集；把桌面半边复制到 `~/.hermes/desktop-plugins/hermes-redteam/`；跑一次 `hermes plugins doctor`。

然后：

1. 重启 dashboard（远程桌面 App 连的是它）：`systemctl --user restart hermes-dashboard.service`
2. 重启 gateway（派工/工具）：`hermes gateway restart`
3. 打开 Hermes desktop → 右上角 **显示右侧栏** → 选择 **RedTeam 控制台**
4. 没有面板时：⌘K → **Reload desktop plugins**

### 方式 B：源码开发

```bash
git clone https://github.com/youzaiooo/Hermes-Redteam-Mode ~/src/hermes-redteam
ln -sfn ~/src/hermes-redteam ~/.hermes/plugins/hermes-redteam
bash ~/src/hermes-redteam/scripts/install.sh
```

桌面半边在开发态由 app 从 checkout 热同步；如果没出现，删掉 `~/.hermes/desktop-plugins/hermes-redteam/.hermes-package.json`（让 app 把它当独立插件加载），再 Reload。

### 远程桌面（桌面端在另一台电脑）

桌面 App 与 Sekhmet 网关不在同一台机器时，**agent half 装在网关，desktop half 装在客户端**：

1. 网关（Kali）按方式 A 安装并 `hermes gateway restart`。
2. 客户端（运行 Hermes desktop 的电脑）：设置 → 插件 → **Install from Git** → `youzaiooo/Hermes-Redteam-Mode` → **勾选 Desktop target** → Reload desktop plugins → 在插件页启用 `hermes-redteam`。
3. 一键安装链接：`hermes://plugin/install?repo=youzaiooo/Hermes-Redteam-Mode&enable=1`

没有 Git 安装入口时，在客户端运行 `scripts/install-desktop.sh`（Windows 用 `scripts/install-desktop.ps1`）。

完整检查清单与排障见 [docs/REMOTE.md](docs/REMOTE.md)。

## 使用

1. 在 Sekhmet（default）会话里说：**靶标单位名 + 范围**。指挥会调用 `redteam_preflight`。
2. 指挥开靶标：`redteam_engagement_open`，让你补 `wiki/authorization.md`（授权方/范围/时间窗/允许手段/联系人）。
3. 指挥按阶段派工：`redteam_dispatch(role=recon|asset|vuln|exploit|internal, task=...)`。
4. `redteam_dispatch_status(task_id)` 跟进；卡片完成后读库核对成果。
5. 右侧面板实时显示：当前得分、五阶段、资产/漏洞/凭据/隧道、worker 角色、报告索引、技能可用性。

## 安全边界

- 没有 `authorization.md` 或关键字段为空，`redteam_dispatch` 拒绝派工。
- 派工卡片带靶标目录与范围，worker 只测卡片内的目标。
- 凭据只存指针/来源，命令正文与 payload 不入库。
- 演练事实不进记忆、不进共享 Wiki；整个靶标目录可直接删除。

## 开发

```bash
env -u PYTHONPATH /usr/bin/python3 -m pytest tests -q
hermes plugins doctor hermes-redteam
node --input-type=module --check < desktop/plugin.js
```

当前状态：M1 注册/派工、M2 中文面板、M3 技能移植、M4 数据模型补全均已完成；端到端已在本机 `127.0.0.1:8765` 验证（指挥开靶标 → 派 `rt-recon` → curl 取标题 → 资产落库 → 面板计数 1）。
