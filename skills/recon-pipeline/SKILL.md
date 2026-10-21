---
name: recon-pipeline
description: Use when the recon-pipeline step is authorized. Store paths and one-line results only.
---

# recon-pipeline

按 `subfinder`、`dnsx`、`naabu`、`httpx` 的顺序跑。每步缺工具就停在预检。

新资产用 `redteam_asset_add` 建索引。扫描正文只留相对路径。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
