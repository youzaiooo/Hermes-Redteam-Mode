"""Make the plugin importable as `hermes_redteam` under pytest.

Hermes loads this plugin by folder name (`hermes-redteam`), which is not a valid
Python identifier, so the suite cannot `import hermes_redteam` from the repo root
on its own. Execute the real package `__init__.py` into an alias module pointing
at the repo root, instead of requiring an external PYTHONPATH or a symlink.
"""

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_PACKAGES = {
    "hermes_redteam": _ROOT,
    "hermes_redteam.dashboard": _ROOT / "dashboard",
}

for _name, _dir in _PACKAGES.items():
    if _name in sys.modules:
        continue

    _init = _dir / "__init__.py"

    if not _init.is_file():
        # Namespace-style directory (e.g. `dashboard/`): no code to execute,
        # only a search path so `hermes_redteam.dashboard.plugin_api` resolves.
        import types

        _module = types.ModuleType(_name)
        _module.__path__ = [str(_dir)]
        sys.modules[_name] = _module
        continue

    _spec = importlib.util.spec_from_file_location(
        _name, _init, submodule_search_locations=[str(_dir)]
    )
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_name] = _module
    _spec.loader.exec_module(_module)
