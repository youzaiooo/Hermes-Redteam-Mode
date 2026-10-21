import json

from hermes_redteam.store import role_list


def test_role_list_returns_five_execution_profiles():
    found = json.loads(role_list())

    assert found["ok"] is True
    assert found["roles"] == [
        "rt-recon",
        "rt-asset",
        "rt-vuln",
        "rt-exploit",
        "rt-internal",
    ]
