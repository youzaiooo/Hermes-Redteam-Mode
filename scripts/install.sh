#!/usr/bin/env bash
# Enable hermes-redteam for the commander and the five permanent worker profiles.
# Safe to re-run. Does not restart the gateway.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES="${HERMES_BIN:-hermes}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

echo "==> plugin dir: $REPO_DIR"
if [ ! -d "$HERMES_HOME/plugins/hermes-redteam" ]; then
  ln -sfn "$REPO_DIR" "$HERMES_HOME/plugins/hermes-redteam"
fi

echo "==> desktop half"
mkdir -p "$HERMES_HOME/desktop-plugins/hermes-redteam"
cp "$REPO_DIR/desktop/plugin.js" "$HERMES_HOME/desktop-plugins/hermes-redteam/plugin.js"
# A bare folder with plugin.js is loaded as a standalone desktop plugin. A stale
# package marker makes the app treat it as a managed copy and skip it.
rm -f "$HERMES_HOME/desktop-plugins/hermes-redteam/.hermes-package.json"

echo "==> sync commander user skill (a stale local copy shadows the plugin)"
COMMANDER_SKILL="$HERMES_HOME/skills/redteam-commander/SKILL.md"
if [ -f "$COMMANDER_SKILL" ]; then
  cp "$COMMANDER_SKILL" "$COMMANDER_SKILL.bak-install" 2>/dev/null || true
  cp "$REPO_DIR/skills/redteam-commander/SKILL.md" "$COMMANDER_SKILL"
fi

echo "==> enable for default + rt-* profiles"
"$HERMES" plugins enable hermes-redteam --no-allow-tool-override >/dev/null 2>&1 || true
for profile in rt-recon rt-asset rt-vuln rt-exploit rt-internal; do
  if "$HERMES" profile list 2>/dev/null | grep -q "$profile"; then
    "$HERMES" -p "$profile" plugins enable hermes-redteam --no-allow-tool-override >/dev/null 2>&1 || true
  fi
done

echo "==> enable the hermes-redteam toolset"
"$HERMES" tools enable hermes-redteam --platform cli >/dev/null 2>&1 || true
"$HERMES" tools enable hermes-redteam --platform desktop >/dev/null 2>&1 || true

echo "==> doctor"
"$HERMES" plugins doctor hermes-redteam 2>&1 | tail -6

cat <<'EOF'

Done. Next:
  1) 重启 dashboard（远程桌面 App 连的是它，新 API 路由才会生效）：
       systemctl --user restart hermes-dashboard.service
     没有 systemd 的话，重启你手动跑的 `hermes dashboard` 进程。
  2) 重启 gateway（派工/工具）：
       hermes gateway restart
  3) Hermes desktop -> 右上角「显示右侧栏」-> RedTeam 控制台
  4) 命令面板 ⌘K -> Reload desktop plugins（如果面板没出现）
EOF

if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  cat <<'EOF'

Note: 当前没有图形会话。如果 Hermes desktop 在另一台电脑上（远程网关场景），
请在**桌面端所在电脑**上安装桌面半边，二选一：
  - App 内：设置 -> 插件 -> Install from Git -> youzaiooo/Hermes-Redteam-Mode
            有 Agent/Desktop 勾选时只勾 Desktop；只有「此包包含」列表时直接安装
            （agent half 会装到已连接的 default 后端，桌面 UI 装到本机）
            已存在时打开「强制重装」-> Reload desktop plugins -> 启用插件
  - 或运行仓库里的 scripts/install-desktop.sh（Windows 用 install-desktop.ps1）
详见 docs/REMOTE.md
EOF
fi
