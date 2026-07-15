import httpx
import os


class OmniverseClient:

    def __init__(self):
        self.nucleus_url = os.getenv("NVIDIA_NUCLEUS_URL", "")
        self.api_key = os.getenv("NVIDIA_API_KEY", "")

    async def subscribe_events(self, scene_id: str) -> dict:
        if not self.nucleus_url:
            return {"status": "not_configured"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.nucleus_url}/api/v1/scenes/{scene_id}/webhooks",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "url": f"{os.getenv('RENDER_URL', 'https://engenheiro-producao-ai.onrender.com')}/api/physical-ai/event",
                    "events": ["simulation_complete", "anomaly_detected", "equipment_state_changed", "production_cycle_complete"]
                }
            )
        return resp.json()

    async def get_sensor_data(self, scene_id: str, sensor_ids: list) -> dict:
        if not self.nucleus_url:
            return {"status": "not_configured"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.nucleus_url}/api/v1/scenes/{scene_id}/sensors",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"ids": ",".join(sensor_ids)}
            )
        return resp.json()
