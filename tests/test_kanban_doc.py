from pathlib import Path


def test_kanban_doc_has_handoff_rules_not_steps():
    text = Path("docs/kanban.md").read_text(encoding="utf-8")

    assert "Sekhmet" in text
    assert "assignee" in text
    assert "payload" in text
    assert "nmap" not in text.lower()
