class DockerIntegration:
    def __init__(self):
        self.client = None

    def build_image(self, tag: str, dockerfile: str = "Dockerfile", path: str = ".") -> dict:
        return {
            "integration": "docker",
            "action": "build",
            "tag": tag,
            "status": "simulated",
        }

    def run_container(self, image: str, name: str = None, ports: dict = None, env: dict = None) -> dict:
        return {
            "integration": "docker",
            "action": "run",
            "image": image,
            "name": name,
            "ports": ports or {},
            "status": "simulated",
        }

    def stop_container(self, container_id: str) -> dict:
        return {
            "integration": "docker",
            "action": "stop",
            "container_id": container_id,
            "status": "simulated",
        }
