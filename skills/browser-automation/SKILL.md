---
name: browser-automation
description: Use when the browser-automation step is authorized. Store paths and one-line results only.
---

# browser-automation

用无头浏览器取页面证据。截图只通过 `redteam_shot_add` 存路径，不存图片正文。

Cookie 不入库。登录态只留在浏览器侧。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
