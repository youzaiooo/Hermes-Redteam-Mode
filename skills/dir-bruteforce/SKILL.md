---
name: dir-bruteforce
description: Use when the dir-bruteforce step is authorized. Store paths and one-line results only.
---

# dir-bruteforce

用 `ffuf`、`feroxbuster`、`dirsearch` 或 `gobuster` 做目录发现。

结果路径写入 `redteam_scan_add`。字典内容和命中正文不入库。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
