# Schema 边界

P0 只规划，不在本轮建表。

## index.db

每靶标一个文件。存：

- engagement：id、显示名、创建时间、绑定的 profile 会话
- asset：稳定键、地址或名称、状态、首次发现、最后见到
- port：资产外键、端口、协议、状态
- evidence_ref：种类、相对路径、sha256、一行结论
- reservation：靶标、角色、占用时间。P1 起使用，软上限 3。P0 不建写入路径。

不存：口令、Cookie、密钥、原始 HTTP 正文、截图字节。

## wiki

`index.md` 是 agent 开工时唯一必读页。单页超过约 200 行就拆。`log.md` 只记动作，不记战果统计。

## 得分

规则定义留在插件代码。命中记录只在 `score_rules` 为 `visible` 或 `enforced` 时出现。`off` 时不建命中行。
