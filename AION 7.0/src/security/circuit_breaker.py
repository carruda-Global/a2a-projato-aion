import time
from typing import Any, Optional


class CircuitBreaker:
    def __init__(self, threshold: int = 5, reset_seconds: int = 60):
        self.threshold = threshold
        self.reset_seconds = reset_seconds
        self.failures: dict[str, int] = {}
        self.last_failure: dict[str, float] = {}
        self.state: dict[str, str] = {}

    def call(self, agent_id: str, func, *args, **kwargs) -> Any:
        state = self.state.get(agent_id, "closed")

        if state == "open":
            if time.time() - self.last_failure.get(agent_id, 0) > self.reset_seconds:
                self.state[agent_id] = "half-open"
            else:
                raise Exception(f"Circuit breaker open for {agent_id}")

        try:
            result = func(*args, **kwargs)
            if self.state.get(agent_id) == "half-open":
                self.state[agent_id] = "closed"
                self.failures[agent_id] = 0
            return result
        except Exception as e:
            self.failures[agent_id] = self.failures.get(agent_id, 0) + 1
            self.last_failure[agent_id] = time.time()

            if self.failures[agent_id] >= self.threshold:
                self.state[agent_id] = "open"

            raise

    async def call_async(self, agent_id: str, func, *args, **kwargs) -> Any:
        state = self.state.get(agent_id, "closed")

        if state == "open":
            if time.time() - self.last_failure.get(agent_id, 0) > self.reset_seconds:
                self.state[agent_id] = "half-open"
            else:
                raise Exception(f"Circuit breaker open for {agent_id}")

        try:
            result = await func(*args, **kwargs)
            if self.state.get(agent_id) == "half-open":
                self.state[agent_id] = "closed"
                self.failures[agent_id] = 0
            return result
        except Exception as e:
            self.failures[agent_id] = self.failures.get(agent_id, 0) + 1
            self.last_failure[agent_id] = time.time()

            if self.failures[agent_id] >= self.threshold:
                self.state[agent_id] = "open"

            raise

    def get_status(self) -> dict:
        return {
            agent_id: {
                "state": self.state.get(agent_id, "closed"),
                "failures": self.failures.get(agent_id, 0),
                "last_failure": self.last_failure.get(agent_id, 0),
            }
            for agent_id in set(list(self.state.keys()) + list(self.failures.keys()))
        }
