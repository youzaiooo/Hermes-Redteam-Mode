"""The desktop half and the gateway manifest must advertise the same version."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _manifest_version() -> str:
    text = (ROOT / "plugin.yaml").read_text(encoding="utf-8")
    match = re.search(r"^version:\s*([^\s#]+)", text, re.MULTILINE)
    assert match, "plugin.yaml has no version"
    return match.group(1).strip("'\"")


def _desktop_version() -> str:
    text = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")
    match = re.search(r"DESKTOP_VERSION\s*=\s*'([^']+)'", text)
    assert match, "desktop/plugin.js has no DESKTOP_VERSION"
    return match.group(1)


def test_desktop_version_matches_manifest():
    assert _desktop_version() == _manifest_version()


def test_version_route_reports_manifest_version():
    spec = importlib.util.spec_from_file_location("hermes_redteam_plugin_api", ROOT / "dashboard" / "plugin_api.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.version_info()["version"] == _manifest_version()
