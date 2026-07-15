import os


class SalesforceIntegration:
    def __init__(self):
        self.instance_url = os.getenv("SALESFORCE_URL", "")
        self.client_id = os.getenv("SALESFORCE_CLIENT_ID", "")
        self.client_secret = os.getenv("SALESFORCE_CLIENT_SECRET", "")

    def create_lead(self, lead_data: dict) -> dict:
        return {
            "integration": "salesforce",
            "action": "create_lead",
            "data": lead_data,
            "status": "simulated",
        }

    def update_opportunity(self, opportunity_id: str, data: dict) -> dict:
        return {
            "integration": "salesforce",
            "action": "update_opportunity",
            "opportunity_id": opportunity_id,
            "data": data,
            "status": "simulated",
        }

    def create_task(self, task_data: dict) -> dict:
        return {
            "integration": "salesforce",
            "action": "create_task",
            "data": task_data,
            "status": "simulated",
        }
