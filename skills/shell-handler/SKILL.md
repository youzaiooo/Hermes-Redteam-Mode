---
name: shell-handler
description: Use when the shell-handler step is authorized. Store paths and one-line results only.
---

# shell-handler

会话建立后用 `redteam_access_add` 记状态。不记监听命令，不记载荷。

断开后回写状态，不把会话正文入库。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
