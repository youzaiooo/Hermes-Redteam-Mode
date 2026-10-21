---
name: fofa-recon
description: Use when the fofa-recon step is authorized. Store paths and one-line results only.
---

# fofa-recon

先确认 `FOFA_KEY` 在环境变量里。没有就停，向用户要，不把密钥写入文件。

查询结果只存相对路径，再用 `redteam_scan_add` 建索引。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
