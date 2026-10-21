import json

from hermes_redteam.score import score_list


def test_score_list_returns_eight_categories_and_twenty_five_points():
    found = json.loads(score_list())

    assert found["ok"] is True
    assert len(found["categories"]) == 8
    assert sum(len(item["points"]) for item in found["categories"]) == 25
