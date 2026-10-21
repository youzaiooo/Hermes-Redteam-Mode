---
name: kimi-webbridge
description: Use when the kimi-webbridge step is authorized. Store paths and one-line results only.
---

# kimi-webbridge

用真实浏览器复用登录态。登录成功后用 `redteam_access_add` 记访问状态。

Token 不入库。只记资产、方法和证据路径。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
