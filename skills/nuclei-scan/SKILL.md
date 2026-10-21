---
name: nuclei-scan
description: Use when the nuclei-scan step is authorized. Store paths and one-line results only.
---

# nuclei-scan

用 `nuclei` 做模板检测。模板路径和结果路径分开存。

命中后用 `redteam_vuln_add` 建漏洞索引。模板正文不入库。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
