---
name: web-fingerprint
description: Use when the web-fingerprint step is authorized. Store paths and one-line results only.
---

# web-fingerprint

用 `httpx` 或浏览器取标题、框架、中间件、CMS 和版本。Kali 自带 `/usr/bin/httpx` 不是 ProjectDiscovery httpx，必须用工具箱绝对路径。

一行结论写入 `redteam_asset_test`。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
