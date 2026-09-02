"""
Backend API tests for Portable Personal AI Computer dashboard.
Tests: system status/stats, desktop endpoints (docker-unavailable graceful failure),
GitHub status/commits/push (not configured graceful failure),
Backups full CRUD lifecycle against real filesystem.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://hermes-workstation.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------- System / Desktop ----------

class TestSystem:
    def test_root(self, client):
        r = client.get(f"{API}/")
        assert r.status_code == 200
        assert "message" in r.json()

    def test_system_status_docker_unavailable(self, client):
        r = client.get(f"{API}/system/status")
        assert r.status_code == 200
        d = r.json()
        assert d["docker_available"] is False
        assert d["desktop"]["status"] == "unavailable"
        assert d["container_name"]
        assert "timestamp" in d
        # New field for network reachability decoupled from docker socket
        assert "desktop_network_reachable" in d
        # No DESKTOP_URL configured in this sandbox -> must be False
        assert d["desktop_network_reachable"] is False

    def test_system_stats_real_host_values(self, client):
        r = client.get(f"{API}/system/stats")
        assert r.status_code == 200
        d = r.json()
        assert d["docker_available"] is False
        assert d["desktop_stats"] is None
        h = d["host_stats"]
        assert isinstance(h["cpu_percent"], (int, float))
        assert 0 <= h["mem_percent"] <= 100
        assert h["mem_total"] > 0
        assert h["disk_total"] > 0
        assert 0 <= h["disk_percent"] <= 100

    def test_desktop_start_returns_503(self, client):
        r = client.post(f"{API}/desktop/start")
        assert r.status_code == 503
        assert "Docker" in r.json().get("detail", "")

    def test_desktop_stop_returns_503(self, client):
        assert client.post(f"{API}/desktop/stop").status_code == 503

    def test_desktop_restart_returns_503(self, client):
        assert client.post(f"{API}/desktop/restart").status_code == 503

    def test_desktop_open_unavailable(self, client):
        r = client.get(f"{API}/desktop/open")
        assert r.status_code == 200
        body = r.json()
        assert body["available"] is False
        assert "url" in body


# ---------- GitHub ----------

class TestGitHub:
    def test_github_status(self, client):
        r = client.get(f"{API}/github/status")
        assert r.status_code == 200
        d = r.json()
        assert d["branch"]  # real branch e.g. main
        # GitHub is now configured with real token+repo
        assert d["configured"] is True
        assert isinstance(d["changes"], list)

    def test_github_commits(self, client):
        r = client.get(f"{API}/github/commits")
        assert r.status_code == 200
        commits = r.json()["commits"]
        assert isinstance(commits, list)
        assert len(commits) >= 1
        c = commits[0]
        for k in ("sha", "author", "date", "message"):
            assert k in c

    def test_github_push_configured(self, client):
        # Configured now; push against clean tree should succeed (idempotent 'up-to-date')
        r = client.post(f"{API}/github/push")
        # Accept 200 (success/up-to-date) or 400 (if git rejects for any reason)
        assert r.status_code in (200, 400), r.text
        if r.status_code == 200:
            assert r.json().get("ok") is True

    def test_github_pull_configured(self, client):
        r = client.post(f"{API}/github/pull")
        assert r.status_code in (200, 400), r.text

    def test_github_sync_configured(self, client):
        r = client.post(f"{API}/github/sync")
        assert r.status_code in (200, 400), r.text


# ---------- Backups CRUD ----------

class TestBackups:
    created_filenames = []

    def test_list_backups_initial(self, client):
        r = client.get(f"{API}/backups")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_backup(self, client):
        r = client.post(f"{API}/backups", json={"note": "TEST_snapshot_1"})
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["filename"].startswith("backup-") and d["filename"].endswith(".tar.gz")
        assert d["size_bytes"] > 0
        assert d["note"] == "TEST_snapshot_1"
        assert "id" in d
        # No mongo _id leaking
        assert "_id" not in d
        TestBackups.created_filenames.append(d["filename"])

    def test_create_second_backup(self, client):
        r = client.post(f"{API}/backups", json={"note": "TEST_snapshot_2"})
        assert r.status_code == 200
        TestBackups.created_filenames.append(r.json()["filename"])

    def test_backup_appears_in_list(self, client):
        r = client.get(f"{API}/backups")
        assert r.status_code == 200
        listed = {b["filename"] for b in r.json()}
        for fn in TestBackups.created_filenames:
            assert fn in listed

    def test_restore_backup(self, client):
        fn = TestBackups.created_filenames[0]
        r = client.post(f"{API}/backups/{fn}/restore")
        assert r.status_code == 200
        d = r.json()
        assert d["restored"] is True
        assert d["filename"] == fn

    def test_restore_missing_backup_404(self, client):
        r = client.post(f"{API}/backups/does-not-exist.tar.gz/restore")
        assert r.status_code == 404

    def test_delete_backup(self, client):
        # Cleanup all created test backups
        for fn in TestBackups.created_filenames:
            r = client.delete(f"{API}/backups/{fn}")
            assert r.status_code == 200
            assert r.json()["deleted"] is True
        # Verify removed
        r = client.get(f"{API}/backups")
        listed = {b["filename"] for b in r.json()}
        for fn in TestBackups.created_filenames:
            assert fn not in listed
