---
name: redteam-preflight
description: "已授权靶标开工前的缺件检查。只报告，不安装。"
version: 0.1.0
---

# Preflight

先读 `wiki/authorization.md`。授权方、范围、时间窗、允许手段、联系人有空项时，状态是 `blocked`。

再检查本机工具：`nmap`、`nuclei`、`sqlmap`、`ffuf`。缺什么就列出来。不自动安装。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
