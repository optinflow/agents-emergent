# Portable Personal AI Computer

Your own always-on, browser-accessible Ubuntu desktop, packaged as Docker +
Docker Compose, controlled by a black-and-white futuristic web dashboard.

The running container is disposable. Everything that matters lives in
`/data` (persistent volumes) and this Git repo. Clone anywhere with Docker,
restore your backup, run one command, and the same computer comes back.

## Repository layout
```
/infrastructure   Dockerfile(s) + docker-compose.yml
/config           non-secret desktop config templates
/scripts          start / stop / rebuild / backup / restore / migrate
/data             persistent volumes (gitignored) - home, browser profile, mongo, backups
.env.example      documents required secrets/vars (committed)
.env              your real secrets (gitignored, never commit)
```
The dashboard itself lives at `/backend` (FastAPI) + `/frontend` (React) at
the repo root rather than nested under `/dashboard`, so it plugs straight
into standard FastAPI/React tooling. Functionally it's the same "dashboard"
component described in the spec.

## Requirements
Any Linux/macOS/Windows host with Docker + Docker Compose. Recommended 8GB
RAM / 4 vCPU / 40-60GB SSD; workable at 4GB/2vCPU (tighter with Chromium).

## First run on a fresh host
```bash
git clone <your-repo-url>
cd <repo>
cp .env.example .env
# edit .env - set GITHUB_TOKEN + GITHUB_REPO_URL if you want the GitHub panel to push/pull
./scripts/start.sh
```
Dashboard: `http://localhost:3000` (or `$FRONTEND_PORT`).
Desktop: `http://localhost:3010` (or `$DESKTOP_PORT`), also reachable via the
dashboard's "Open Desktop" button.

## Scripts
- `./scripts/start.sh` - `docker compose up -d`
- `./scripts/stop.sh` - graceful `docker compose down` (volumes untouched)
- `./scripts/rebuild.sh` - rebuild images from the Dockerfiles, data untouched
- `./scripts/backup.sh` - timestamped `tar.gz` of `./data` into `./data/backups`
- `./scripts/restore.sh <archive>` - extract a backup archive back into `./data`
- `./scripts/migrate.sh <archive>` - verify Docker → restore → load `.env` → start

## Migration flow (the portability test)
1. `git clone` this repo on any Docker+Compose host
2. Copy a backup archive onto that host
3. `./scripts/restore.sh <backup.tar.gz>`
4. `cp .env.example .env` and fill in secrets
5. `./scripts/start.sh`
6. Same computer is back: files, browser profile, apps, configs intact

## The desktop container
`infrastructure/Dockerfile.desktop` extends
`lscr.io/linuxserver/webtop:ubuntu-xfce` (Ubuntu + XFCE + KasmVNC,
browser-based remote desktop, no systemd - everything runs under
s6-overlay). The home directory is bind-mounted to `./data/home` so it
survives `down`/`up`/`rebuild`.

## Dashboard
FastAPI backend controls the desktop container over the Docker socket
(`/var/run/docker.sock`), and exposes backup/restore, resource stats
(`docker stats`-equivalent), and a GitHub push/pull/sync panel. The React
frontend is the black-and-white futuristic control panel.

**Environment note:** this dashboard was developed inside a sandbox with no
Docker socket access. Every Docker-dependent feature (start/stop/restart,
live stats, embedded desktop/terminal) detects the missing daemon and
honestly reports "Docker unavailable" instead of faking data. Deploy the
same, unmodified code via `infrastructure/docker-compose.yml` on a real
Docker host and every feature works against the real desktop container. The
GitHub panel and backup/restore already work in either environment since
they only touch the filesystem/git.

## GitHub integration
Set `GITHUB_TOKEN` (fine-grained PAT scoped to one repo, Contents: Read and
write - create one at https://github.com/settings/tokens?type=beta) and
`GITHUB_REPO_URL` in `.env`. The dashboard's Push button auto-commits any
pending changes and pushes; Pull rebases from origin; Sync does both. The
token never reaches the browser - it's only ever used server-side.

## Backups
`POST /api/backups` tars up everything under `DATA_DIR` (excluding
`backups/`) into a timestamped `.tar.gz`, cataloged in MongoDB. Restore
extracts a chosen archive back over `DATA_DIR`. Exercise `restore`
regularly - an untested backup isn't a backup.

## Security notes
- `.env`, `/data`, and `*.tar.gz` are gitignored - never commit secrets or backups.
- Scope the GitHub token to a single repository.
- No dashboard auth in this phase (single-user/private) - don't expose the
  dashboard port to the public internet.
