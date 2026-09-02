import os
import stat
import tempfile
import subprocess
from pathlib import Path


class GitHubManager:
    def __init__(self, repo_dir, token, remote_url, branch):
        self.repo_dir = Path(repo_dir)
        self.token = token
        self.remote_url = remote_url
        self.branch = branch or "main"

    def is_configured(self):
        return bool(self.token and self.remote_url)

    def _env(self):
        env = os.environ.copy()
        askpass_path = None
        if self.token:
            script = tempfile.NamedTemporaryFile("w", delete=False, prefix="git-askpass-", suffix=".sh")
            script.write('#!/bin/sh\ncase "$1" in *Username*) echo x-access-token;; *) echo "$GITHUB_TOKEN";; esac\n')
            script.close()
            os.chmod(script.name, os.stat(script.name).st_mode | stat.S_IXUSR)
            askpass_path = script.name
            env["GIT_ASKPASS"] = askpass_path
            env["GITHUB_TOKEN"] = self.token
        env["GIT_TERMINAL_PROMPT"] = "0"
        return env, askpass_path

    def _run(self, *args):
        env, askpass_path = self._env()
        try:
            proc = subprocess.run(
                ["git", *args], cwd=self.repo_dir, env=env, text=True,
                capture_output=True, timeout=60, check=False,
            )
        finally:
            if askpass_path:
                Path(askpass_path).unlink(missing_ok=True)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip()[:500] or f"git {' '.join(args)} failed")
        return proc.stdout.strip()

    def is_git_repo(self):
        return (self.repo_dir / ".git").exists()

    def status(self):
        if not self.is_git_repo():
            return {
                "branch": None,
                "clean": True,
                "changes": [],
                "remote_url": "",
                "configured": self.is_configured(),
                "git_repo_found": False,
            }
        branch = self._run("branch", "--show-current")
        porcelain = self._run("status", "--porcelain")
        try:
            remote_url = self._run("remote", "get-url", "origin")
        except RuntimeError:
            remote_url = ""
        return {
            "branch": branch,
            "clean": not porcelain,
            "changes": [l for l in porcelain.splitlines() if l],
            "remote_url": remote_url,
            "configured": self.is_configured(),
            "git_repo_found": True,
        }

    def commits(self, limit=10):
        try:
            out = self._run("log", f"-{limit}", "--date=iso-strict", "--pretty=format:%H%x09%an%x09%ad%x09%s")
        except RuntimeError:
            return []
        result = []
        for line in out.splitlines():
            parts = line.split("\t", 3)
            if len(parts) == 4:
                result.append({"sha": parts[0], "author": parts[1], "date": parts[2], "message": parts[3]})
        return result

    def _ensure_remote(self):
        try:
            self._run("remote", "get-url", "origin")
            self._run("remote", "set-url", "origin", self.remote_url)
        except RuntimeError:
            self._run("remote", "add", "origin", self.remote_url)

    def push(self, commit_message=None):
        if not self.is_configured():
            raise RuntimeError("GitHub not configured: set GITHUB_TOKEN and GITHUB_REPO_URL in backend/.env")
        if not self.is_git_repo():
            raise RuntimeError("No .git directory found on this host - this deployment has no git history to push")
        porcelain = self._run("status", "--porcelain")
        if porcelain:
            self._run("add", "-A")
            self._run("commit", "-m", commit_message or "chore: dashboard auto-sync")
        self._ensure_remote()
        return self._run("push", "-u", "origin", f"HEAD:{self.branch}")

    def pull(self):
        if not self.is_configured():
            raise RuntimeError("GitHub not configured: set GITHUB_TOKEN and GITHUB_REPO_URL in backend/.env")
        if not self.is_git_repo():
            raise RuntimeError("No .git directory found on this host - this deployment has no git history to pull into")
        self._ensure_remote()
        return self._run("pull", "--rebase", "origin", self.branch)

    def sync(self):
        pull_out = self.pull()
        push_out = self.push()
        return {"pull": pull_out, "push": push_out}
