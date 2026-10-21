---
name: asset-correlation
description: Use when the asset-correlation step is authorized. Store paths and one-line results only.
---

# asset-correlation

把域名、IP、C 段、证书和服务关系写入 `redteam_asset_link`。

需要看全图时读 `redteam_asset_graph`。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
