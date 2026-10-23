def test_dashboard_exposes_read_routes():
    from hermes_redteam.dashboard.plugin_api import router

    paths = sorted(route.path for route in router.routes)

    assert paths == [
        "/assets/{engagement_id}",
        "/board/{engagement_id}",
        "/credentials/{engagement_id}",
        "/engagements",
        "/engagements/current",
        "/engagements/for-session/{session_id}",
        "/findings/{engagement_id}",
        "/report/{engagement_id}",
        "/roles",
        "/score-rules",
        "/score-rules",
        "/sessions/{engagement_id}",
        "/skills",
        "/summary/{engagement_id}",
        "/tunnels/{engagement_id}",
        "/version",
    ]
