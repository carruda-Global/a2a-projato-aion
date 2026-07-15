import os


class SlackIntegration:
    def __init__(self):
        self.token = os.getenv("SLACK_TOKEN", "")
        self.channel = os.getenv("SLACK_CHANNEL", "general")

    def send_message(self, text: str, channel: str = None) -> dict:
        return {
            "integration": "slack",
            "action": "send_message",
            "channel": channel or self.channel,
            "status": "simulated",
        }

    def send_notification(self, title: str, message: str, color: str = "#36a64f") -> dict:
        return {
            "integration": "slack",
            "action": "send_notification",
            "title": title,
            "status": "simulated",
        }
