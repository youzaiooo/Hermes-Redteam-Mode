---
name: passive-recon
description: Use when the passive-recon step is authorized. Store paths and one-line results only.
---

# passive-recon

只用 `crt.sh`、`dig`、`whois` 做被动收集。不接触目标。

域名、子域、IP、C 段关系写入 `redteam_domain_index`。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
