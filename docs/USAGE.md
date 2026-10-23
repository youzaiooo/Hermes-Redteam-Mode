# 使用说明

## 0. 前提

- Hermes Agent 已安装并能 `hermes gateway status` 看到 running。
- 已创建五个 profile：`rt-recon`、`rt-asset`、`rt-vuln`、`rt-exploit`、`rt-internal`。
  每个 profile 需要自己的模型（建议 `deepseek-v4-pro`）与 `.env` 里的模型 key。
- 本机工具链：`nmap`、`nuclei`（模板库）、`ffuf`/`feroxbuster`、`httpx` 等按需安装；
  `redteam_preflight` 会列出缺什么。

## 1. 启用

```bash
bash ~/.hermes/plugins/hermes-redteam/scripts/install.sh
hermes gateway restart
```

桌面端：右上角 **显示右侧栏** → **RedTeam 控制台**。
如果插件列表里没有：⌘K → **Reload desktop plugins**。

## 2. 开靶标

在 **default（Sekhmet）** 会话里说：

> 目标：<单位名>，范围：<IP/域名/C 段>，时间窗：<...>，允许手段：<...>

指挥会：

1. `redteam_preflight` 做工具与授权预检；
2. `redteam_engagement_open` 建靶标目录；
3. 让你补 `wiki/authorization.md`（五个字段必填）。

也可以直接让指挥创建授权页，然后你自己用编辑器补：

```
$HERMES_HOME/redteam/engagements/<id>/wiki/authorization.md
```

## 3. 派工

指挥按阶段调用：

```json
redteam_dispatch {
  "role": "recon",
  "task": "只测 10.0.0.0/24 的 80/443/8080，收集标题与框架，逐条落库",
  "title": "recon: 10.0.0.0/24"
}
```

返回卡片 id。用 `redteam_dispatch_status {"task_id": "t_..."}` 跟进。
同一靶标最多 3 个在跑卡片；被拒就等现有卡片完成。

阶段顺序：`recon → asset → vuln → exploit → internal`。
单资产（一个 IP/URL）只派 `vuln → exploit`。

## 4. 看结果

右侧面板：

| 页签 | 内容 |
|---|---|
| 态势 | 当前得分、五阶段、五个 worker 角色 |
| 资产 | 地址 / 端口 / 服务 / 标题 / 状态 |
| 成果 | 漏洞标题 / 等级 / 资产 / 状态 + 凭据/隧道计数 |
| 报告 | 报告索引 |
| 资源 | 技能可用性、角色 |

面板跟随当前会话：切到哪个会话，就显示那个会话绑定的靶标。
**新会话默认不绑定靶标**：控制台显示“未绑定靶标”，不会继承上一次演练；要看历史演练时点“手动查看最近演练”，右上角 × 清除手动选择。

## 5. 常见问题

**派工返回 `authorization_required`**
授权页缺失或五个字段有空值。补 `wiki/authorization.md` 后重试。

**派工返回 `session_unbound`**
当前会话还没绑定靶标。让指挥先 `redteam_session_bind`，或在 `redteam_dispatch` 里显式传 `engagement_id`。

**卡片一直 running**
`hermes kanban show <id>` 看 worker 进程；`hermes -p rt-recon chat -q "ping"` 检查该 profile 的模型是否可用。
模型源 503 时 worker 会一直重试，换 provider 或换模型后重新派。

**面板不出现**
右上角先点 **显示右侧栏**；再 ⌘K → **Reload desktop plugins**。
如果桌面半边是从包复制来的，删掉 `~/.hermes/desktop-plugins/hermes-redteam/.hermes-package.json` 让它按独立插件加载。

**doctor 显示 0 tools**
检查 `hermes plugins doctor hermes-redteam` 的 profile 解析；旧版本插件读不到 `ctx.profile_name`，本仓库已改用 `hermes_cli.profiles.current_profile_name()`。

## 6. 清理

一个靶标的全部事实都在：

```
$HERMES_HOME/redteam/engagements/<id>/
├── index.db
├── wiki/
└── raw/
```

演练结束直接删除该目录即可；不会影响其它靶标，也不会写入记忆或共享 Wiki。
