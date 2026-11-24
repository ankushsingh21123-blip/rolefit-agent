"""API: health, jobs, chat, evaluate."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_and_jobs(agent):
    with TestClient(create_app(agent)) as client:
        health = client.get("/health")
        assert health.status_code == 200
        body = health.json()
        assert body["status"] == "ok"
        assert body["jobs_indexed"] == 30
        assert body["demo_mode"] is True
        assert body["llm_provider"] == "stub-demo-only"

        jobs = client.get("/jobs")
        assert jobs.status_code == 200
        assert len(jobs.json()) == 30

        remote = client.get("/jobs", params={"work_mode": "Remote"})
        assert remote.status_code == 200
        assert all(j["work_mode"] == "Remote" for j in remote.json())


def test_chat_endpoint(agent):
    with TestClient(create_app(agent)) as client:
        response = client.post(
            "/chat",
            json={"message": "I want a part-time data analyst job in Bengaluru. I know SQL and Excel."},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["jobs"][0]["job"]["id"] == "job-04"
        assert body["profile"]["locations"] == ["Bengaluru"]


def test_evaluate_endpoint(agent):
    with TestClient(create_app(agent)) as client:
        response = client.post("/evaluate")
        assert response.status_code == 200
        body = response.json()
        assert body["hit_at_3"] == 1.0
        assert body["violation_count"] == 0


def test_demo_page(agent):
    with TestClient(create_app(agent)) as client:
        response = client.get("/demo")
        assert response.status_code == 200
        assert "RoleFit Agent" in response.text
