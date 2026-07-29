from __future__ import annotations

import pytest


@pytest.mark.skip(reason="E2E: requires server running at http://localhost:8000")
def test_frontend_loads(page):
    page.goto("http://localhost:8000/")
    page.wait_for_load_state("networkidle")
    assert page.title() == "Cronos"
    assert page.locator("#root").is_visible()


@pytest.mark.skip(reason="E2E: requires server running at http://localhost:8000")
def test_api_health(page):
    resp = page.request.get("http://localhost:8000/health")
    assert resp.ok
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.skip(reason="E2E: requires server running at http://localhost:8000")
def test_login_flow(page):
    page.goto("http://localhost:8000/")
    page.wait_for_load_state("networkidle")
    page.fill('input[type="text"]', "admin")
    page.fill('input[type="password"]', "admin123")
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    assert page.locator(".kpi-grid").is_visible()
