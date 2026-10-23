# 远程桌面部署（Hermes desktop ↔ 远程 Sekhmet 网关）

适用场景：**桌面 App 在你自己的电脑上**，Sekhmet 网关跑在 Kali（WireGuard 内网 `192.168.10.142:9119`）。

远程模式下，插件的两半分别装在两台机器：

| 半边 | 装在哪 | 作用 |
|---|---|---|
| agent half（`plugin.yaml`、19 个工具、`dashboard/plugin_api.py`） | **网关**（Kali） | 指挥工具、派工、靶标事实库、面板数据 API |
| desktop half（`desktop/plugin.js`） | **桌面端所在电脑** | 右侧 RedTeam 控制台 UI；所有数据通过 `ctx.rest` 走当前网关 |

> 桌面插件是 app 级的。远端的 `~/.hermes/plugins/` 不能被客户端当文件系统访问，所以桌面半边必须在客户端单独安装一次。

## 1. 网关侧（Kali，Sekhmet）

```bash
hermes plugins install youzaiooo/Hermes-Redteam-Mode --enable
bash ~/.hermes/plugins/hermes-redteam/scripts/install.sh
hermes gateway restart
hermes plugins doctor hermes-redteam     # 应为 19 tools
```

网关需要监听 WireGuard 可达的地址。确认：

```bash
ss -ltnp | grep 9119
# 0.0.0.0:9119 或 WireGuard 地址即可；只监听 127.0.0.1 时远端连不上
```

## 2. 桌面侧（你自己的电脑）

### 方式 A：App 内 Install from Git（推荐）

1. Hermes desktop → 设置 → **插件 / Capabilities → Plugins**
2. **Install from Git**
3. 仓库填：`youzaiooo/Hermes-Redteam-Mode`
4. **勾选 Desktop target**（只装桌面半边；agent half 已经在网关上）
5. 安装后：命令面板（`Ctrl/⌘ + K`）→ **Reload desktop plugins**
6. **Capabilities → Plugins → hermes-redteam → 打开**（桌面半边默认是关闭的）

也可以直接打开这个一键链接（在桌面端所在电脑上点）：

```text
hermes://plugin/install?repo=youzaiooo/Hermes-Redteam-Mode&enable=1
```

### 方式 B：手动复制（没有 Git 安装入口时）

Linux / macOS（在客户端执行）：

```bash
bash scripts/install-desktop.sh
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-desktop.ps1
```

然后 `Ctrl/⌘ + K` → **Reload desktop plugins** → 在插件页启用 `hermes-redteam`。

### 版本不一致时

面板顶部会出现一条提示：`客户端 UI vX · 网关 vY`，旁边是 **更新本地 UI** 按钮。点它会让 App 直接用 `installDesktopPlugin` 从 GitHub 重装桌面半边，不需要记命令。更新后如果面板没自动刷新，再按一次 `Ctrl/⌘ + K` → Reload desktop plugins。

## 3. 验证远程链路

1. 桌面 App 已连接到**远程网关**（不是本机 localhost）。
2. 打开 Sekhmet 的已绑定会话 → 右侧 **显示右侧栏** → **RedTeam 控制台**。
3. 面板应显示该会话绑定的靶标数据；新会话应显示「未绑定靶标」。
4. 报告页 → 导出 Markdown：远程模式下走 `captureGatewayFileDownload`，由 App 下载，不依赖网关本地路径。
5. 面板上的「终端」是 App 自己的终端；实际命令仍在网关/Kali 执行。

## 4. 排障

| 现象 | 检查 |
|---|---|
| 面板完全没出现 | 客户端 `~/.hermes/desktop-plugins/hermes-redteam/plugin.js` 是否存在；`Ctrl/⌘+K` → Reload desktop plugins；插件页是否有加载报错 |
| 插件页显示 `unavailable (remote backend)` | 桌面半边没装：用 Install from Git 并勾选 **Desktop target**，或跑 `install-desktop.sh` |
| 面板出现但没有数据 | 网关侧 `hermes plugins doctor hermes-redteam` 是否 19 tools；当前会话是否绑定靶标；网关是否已 `gateway restart` |
| 一直 401 / 登录页 | 桌面 App 没有登录远程网关；先在 App 里完成网关登录（远程用 native bearer，不是本地 cookie） |
| 远端连不上 9119 | WireGuard 是否通；网关是否监听 `0.0.0.0:9119`；防火墙是否放行 |

## 5. 版本要一致

网关执行 `hermes plugins update hermes-redteam` 后，客户端也要更新桌面半边（重新 Install from Git，或点面板顶部的 **更新本地 UI**）。面板会对比 `plugin.yaml` 版本和桌面代码里的 `DESKTOP_VERSION`，不一致时显示 `客户端 UI vX · 网关 vY` 并给出更新按钮；网关断开时页脚提示「显示上次数据」。

## 6. 为什么面板不会读本地文件

`desktop/plugin.js` 只调用 `ctx.rest('/…')`（网关 API）和 `captureGatewayFileDownload()`（网关文件下载）。它不读客户端本地路径，也不假设网关和 App 在同一台机器，所以同一份桌面半边可以同时用于本机和远程。
