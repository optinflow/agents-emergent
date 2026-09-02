from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
import httpx
import psutil
import shutil
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from models import BackupRecord
from docker_manager import docker_manager
from github_manager import GitHubManager
from backup_manager import BackupManager


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

DESKTOP_CONTAINER_NAME = os.environ.get('DESKTOP_CONTAINER_NAME', 'personal-ai-desktop')
DESKTOP_URL = os.environ.get('DESKTOP_URL', '')
DATA_DIR = os.environ.get('DATA_DIR', str(ROOT_DIR.parent / 'data'))
BACKUP_DIR = os.environ.get('BACKUP_DIR', str(Path(DATA_DIR) / 'backups'))
GIT_REPO_DIR = os.environ.get('GIT_REPO_DIR', str(ROOT_DIR.parent))
GIT_BRANCH = os.environ.get('GIT_BRANCH', 'main')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO_URL = os.environ.get('GITHUB_REPO_URL', '')

github_manager = GitHubManager(GIT_REPO_DIR, GITHUB_TOKEN, GITHUB_REPO_URL, GIT_BRANCH)
backup_manager = BackupManager(DATA_DIR, BACKUP_DIR)

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ---------- System / Desktop ----------

@api_router.get("/")
async def root():
    return {"message": "Personal AI Computer Dashboard API"}


async def check_desktop_network_reachable():
    if not DESKTOP_URL:
        return False
    try:
        async with httpx.AsyncClient(timeout=3.0) as http_client:
            resp = await http_client.get(DESKTOP_URL)
            return resp.status_code < 500
    except Exception:
        return False


def get_container_memory():
    """Prefer the cgroup memory limit/usage (accurate inside a container) over
    psutil.virtual_memory(), which reports the shared host's totals on
    platforms like Railway where many containers share one physical node."""
    host_mem = psutil.virtual_memory()
    for current_path, limit_path in [
        ("/sys/fs/cgroup/memory.current", "/sys/fs/cgroup/memory.max"),
        ("/sys/fs/cgroup/memory/memory.usage_in_bytes", "/sys/fs/cgroup/memory/memory.limit_in_bytes"),
    ]:
        try:
            with open(current_path) as f:
                used = int(f.read().strip())
            with open(limit_path) as f:
                raw_limit = f.read().strip()
            if raw_limit == "max":
                continue
            limit = int(raw_limit)
            if 0 < limit < host_mem.total:
                return used, limit
        except (FileNotFoundError, ValueError, PermissionError):
            continue
    return host_mem.used, host_mem.total


@api_router.get("/system/status")
async def system_status():
    desktop = docker_manager.get_desktop_status(DESKTOP_CONTAINER_NAME)
    network_reachable = await check_desktop_network_reachable()
    return {
        "docker_available": docker_manager.is_available(),
        "desktop": desktop,
        "desktop_network_reachable": network_reachable,
        "container_name": DESKTOP_CONTAINER_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@api_router.get("/system/stats")
async def system_stats():
    desktop_stats = docker_manager.get_stats(DESKTOP_CONTAINER_NAME) if docker_manager.is_available() else None
    host_cpu = psutil.cpu_percent(interval=0.3)
    mem_used, mem_total = get_container_memory()
    disk_path = DATA_DIR if Path(DATA_DIR).exists() else "/"
    host_disk = shutil.disk_usage(disk_path)
    return {
        "docker_available": docker_manager.is_available(),
        "desktop_stats": desktop_stats,
        "host_stats": {
            "cpu_percent": host_cpu,
            "mem_percent": round((mem_used / mem_total) * 100, 1) if mem_total else 0.0,
            "mem_used": mem_used,
            "mem_total": mem_total,
            "disk_percent": round((host_disk.used / host_disk.total) * 100, 1),
            "disk_used": host_disk.used,
            "disk_total": host_disk.total,
        },
    }


def _require_docker():
    if not docker_manager.is_available():
        raise HTTPException(status_code=503, detail="Docker daemon not available in this environment")


@api_router.post("/desktop/start")
async def desktop_start():
    _require_docker()
    try:
        return {"status": docker_manager.start_desktop(DESKTOP_CONTAINER_NAME)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/desktop/stop")
async def desktop_stop():
    _require_docker()
    try:
        return {"status": docker_manager.stop_desktop(DESKTOP_CONTAINER_NAME)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/desktop/restart")
async def desktop_restart():
    _require_docker()
    try:
        return {"status": docker_manager.restart_desktop(DESKTOP_CONTAINER_NAME)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/desktop/open")
async def desktop_open():
    reachable = await check_desktop_network_reachable()
    return {"available": reachable, "url": DESKTOP_URL}


@app.websocket("/api/desktop/terminal/ws")
async def desktop_terminal_ws(websocket: WebSocket):
    await websocket.accept()
    if not docker_manager.is_available():
        await websocket.send_text(
            "\r\n[Docker daemon not available in this environment. Deploy this stack on a Docker host to use the terminal.]\r\n"
        )
        await websocket.close()
        return
    try:
        sock = docker_manager.start_exec_session(DESKTOP_CONTAINER_NAME)
    except Exception as e:
        await websocket.send_text(f"\r\n[error starting terminal session: {e}]\r\n")
        await websocket.close()
        return

    loop = asyncio.get_event_loop()
    raw_sock = getattr(sock, "_sock", sock)

    async def reader():
        try:
            while True:
                data = await loop.run_in_executor(None, raw_sock.recv, 4096)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception:
            pass

    reader_task = asyncio.create_task(reader())
    try:
        while True:
            data = await websocket.receive_text()
            raw_sock.send(data.encode())
    except WebSocketDisconnect:
        pass
    finally:
        reader_task.cancel()
        try:
            raw_sock.close()
        except Exception:
            pass


# ---------- Backups ----------

class BackupCreateRequest(BaseModel):
    note: Optional[str] = None


@api_router.get("/backups")
async def list_backups():
    records = await db.backups.find({}).sort("created_at", -1).to_list(200)
    return [BackupRecord.from_mongo(r).model_dump(by_alias=False) for r in records]


@api_router.post("/backups")
async def create_backup(payload: BackupCreateRequest):
    try:
        result = backup_manager.create_backup(note=payload.note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    record = BackupRecord(**result)
    doc = record.to_mongo()
    inserted = await db.backups.insert_one(doc)
    doc["_id"] = inserted.inserted_id
    return BackupRecord.from_mongo(doc).model_dump(by_alias=False)


@api_router.post("/backups/{filename}/restore")
async def restore_backup(filename: str):
    try:
        backup_manager.restore_backup(filename)
        return {"restored": True, "filename": filename}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/backups/{filename}")
async def delete_backup(filename: str):
    backup_manager.delete_backup(filename)
    await db.backups.delete_one({"filename": filename})
    return {"deleted": True}


# ---------- GitHub ----------

@api_router.get("/github/status")
async def github_status():
    try:
        return github_manager.status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/github/commits")
async def github_commits(limit: int = 10):
    return {"commits": github_manager.commits(limit=limit)}


@api_router.post("/github/push")
async def github_push():
    try:
        return {"ok": True, "output": github_manager.push()}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/github/pull")
async def github_pull():
    try:
        return {"ok": True, "output": github_manager.pull()}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/github/sync")
async def github_sync():
    try:
        return {"ok": True, **github_manager.sync()}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
