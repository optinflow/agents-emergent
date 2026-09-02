import logging
import docker
from docker.errors import DockerException, NotFound

logger = logging.getLogger(__name__)


class DockerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()
            self.available = True
        except Exception as e:
            logger.warning(f"Docker daemon not available: {e}")
            self.client = None
            self.available = False

    def is_available(self):
        return self.available

    def get_desktop_status(self, container_name):
        if not self.available:
            return {"status": "unavailable", "image": None, "created": None}
        try:
            container = self.client.containers.get(container_name)
            attrs = container.attrs
            return {
                "status": container.status,
                "image": attrs.get("Config", {}).get("Image"),
                "created": attrs.get("Created"),
            }
        except NotFound:
            return {"status": "not_found", "image": None, "created": None}
        except DockerException as e:
            return {"status": "error", "error": str(e), "image": None, "created": None}

    def start_desktop(self, container_name):
        container = self.client.containers.get(container_name)
        container.start()
        container.reload()
        return container.status

    def stop_desktop(self, container_name):
        container = self.client.containers.get(container_name)
        container.stop()
        container.reload()
        return container.status

    def restart_desktop(self, container_name):
        container = self.client.containers.get(container_name)
        container.restart()
        container.reload()
        return container.status

    def get_stats(self, container_name):
        if not self.available:
            return None
        try:
            container = self.client.containers.get(container_name)
            raw = container.stats(stream=False)
            cpu_delta = raw["cpu_stats"]["cpu_usage"]["total_usage"] - raw["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = raw["cpu_stats"]["system_cpu_usage"] - raw["precpu_stats"]["system_cpu_usage"]
            online_cpus = raw["cpu_stats"].get("online_cpus", 1) or 1
            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0
            mem_usage = raw["memory_stats"].get("usage", 0)
            mem_limit = raw["memory_stats"].get("limit", 1) or 1
            return {
                "cpu_percent": round(cpu_percent, 1),
                "mem_used": mem_usage,
                "mem_limit": mem_limit,
                "mem_percent": round((mem_usage / mem_limit) * 100.0, 1),
            }
        except (NotFound, DockerException) as e:
            logger.warning(f"stats unavailable: {e}")
            return None

    def start_exec_session(self, container_name, cmd=None):
        container = self.client.containers.get(container_name)
        exec_cmd = cmd or ["/bin/bash"]
        exec_id = self.client.api.exec_create(
            container.id, exec_cmd, stdin=True, tty=True
        )["Id"]
        sock = self.client.api.exec_start(exec_id, tty=True, socket=True)
        return sock


docker_manager = DockerManager()
