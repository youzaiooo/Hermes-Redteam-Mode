# hermes-redteam

Hermes agent 插件 + 桌面面板，用来记录**已授权**演练的资产、漏洞、访问、隧道与报告索引。

插件只做编排与索引：不内置 exploit、payload、凭据真值或 WebShell 管理器。演练事实落在 `$HERMES_HOME/redteam/engagements/<id>/`，不进仓库、不进共享 Wiki、不进记忆。

## 结构

```
plugin.yaml            # 插件清单（56 个工具声明）
__init__.py            # register(ctx) 入口
store.py               # SQLite 索引：资产/漏洞/访问/隧道/报告
tools.py               # 工具注册
score.py               # 三档得分开关：off / visible / enforced
preflight.py           # 授权预检
roles/                 # 五个执行角色的提示词
skills/                # 24 个角色技能
dashboard/
  manifest.json
  plugin_api.py        # 只读路由，挂在 /api/plugins/hermes-redteam/
desktop/
  plugin.js            # 桌面面板（Hermes desktop 的 UI 半边）
tests/
SPEC.md  PLAN.md  SESSION.md
```

## 安装

### 1. 插件本体（网关侧）

```bash
git clone <this-repo> ~/.hermes/plugins/hermes-redteam
hermes plugins doctor hermes-redteam     # 确认工具注册
```

然后在该 profile 的 `config.yaml` 里 enable（`plugins.enabled` 加 `hermes-redteam`）。
`/api/plugins/hermes-redteam/*` 只在这个开关打开时才会挂载。

### 2. 桌面面板（每台客户端各一份）

桌面插件由客户端本地磁盘加载，网关不推送。所以每台要连的 Hermes desktop 都要有这份文件：

```bash
mkdir -p ~/.hermes/desktop-plugins/hermes-redteam
cp desktop/plugin.js ~/.hermes/desktop-plugins/hermes-redteam/plugin.js
```

然后在 app 里 ⌘K → **Reload desktop plugins**，再去 Settings → Plugins 打开「红队面板」。

面板是 `defaultEnabled: false`，每台默认关闭，需要手动开一次。
目录名必须等于 `hermes-redteam`。

远程客户端同理：面板走 `ctx.rest` 打**当前连接的网关**，所以网关那侧必须装好插件本体并 enable。

### 3. 得分开关

默认 `off`。面板里切换会写 `config.yaml` 的 `plugins.entries.hermes-redteam.score_rules`，新会话生效。

## 测试

```bash
python3 -m pytest tests -q
```

## 边界

- 只服务已授权演练。开靶标先写 `wiki/authorization.md`，授权为空则预检返回 `blocked`。
- 不落凭据真值、命令文本、PoC 正文。
- 报告索引只含相对路径。
