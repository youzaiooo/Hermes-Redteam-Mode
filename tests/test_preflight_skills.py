import json

from hermes_redteam.preflight import preflight


def test_preflight_reports_skill_catalog(tmp_path):
    from hermes_redteam.store import open_engagement

    open_engagement(tmp_path, "lab-01", "Lab 01")
    found = json.loads(preflight(tmp_path, "lab-01"))

    assert found["skill_count"] == 24
    assert "fofa-recon" in found["skills"]
