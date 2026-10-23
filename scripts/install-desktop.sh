#!/usr/bin/env bash
# Install the desktop half of hermes-redteam on the machine running Hermes desktop.
# Use this when the gateway is remote (e.g. Sekhmet on Kali over WireGuard).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
DEST="$HERMES_HOME/desktop-plugins/hermes-redteam"

mkdir -p "$DEST"
cp "$ROOT/desktop/plugin.js" "$DEST/plugin.js"
rm -f "$DEST/.hermes-package.json"

echo "desktop half installed: $DEST/plugin.js"
echo
echo "Next:"
echo "  1) Hermes desktop -> Ctrl/Cmd+K -> Reload desktop plugins"
echo "  2) Capabilities -> Plugins -> hermes-redteam -> enable"
echo "  3) Right sidebar -> RedTeam 控制台"
