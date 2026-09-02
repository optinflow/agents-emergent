import tarfile
from pathlib import Path
from datetime import datetime, timezone


class BackupManager:
    def __init__(self, data_dir, backup_dir):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, note=None):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"backup-{timestamp}.tar.gz"
        archive_path = self.backup_dir / filename
        volumes = [p.name for p in self.data_dir.iterdir() if p.is_dir() and p.name != "backups"]
        with tarfile.open(archive_path, "w:gz") as tar:
            for vol in volumes:
                tar.add(self.data_dir / vol, arcname=vol)
        return {
            "filename": filename,
            "size_bytes": archive_path.stat().st_size,
            "volumes": volumes,
            "note": note,
        }

    def restore_backup(self, filename):
        archive_path = self.backup_dir / filename
        if not archive_path.exists():
            raise FileNotFoundError(f"backup {filename} not found")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(self.data_dir, filter="data")
        return True

    def delete_backup(self, filename):
        archive_path = self.backup_dir / filename
        if archive_path.exists():
            archive_path.unlink()
            return True
        return False
