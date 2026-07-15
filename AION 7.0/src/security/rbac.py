from typing import Any, Optional


class RBACManager:
    def __init__(self):
        self.roles = {
            "admin": {"permissions": ["read", "write", "delete", "manage", "admin"]},
            "manager": {"permissions": ["read", "write", "manage"]},
            "operator": {"permissions": ["read", "write"]},
            "viewer": {"permissions": ["read"]},
        }
        self.users: dict[str, dict] = {}

    def add_user(self, user_id: str, role: str, tenant_id: str = "default") -> None:
        if role not in self.roles:
            raise ValueError(f"Role '{role}' not found")
        self.users[user_id] = {
            "role": role,
            "tenant_id": tenant_id,
            "permissions": self.roles[role]["permissions"],
        }

    def check_permission(self, user_id: str, permission: str) -> bool:
        user = self.users.get(user_id)
        if not user:
            return False
        return permission in user["permissions"]

    def get_user_role(self, user_id: str) -> Optional[str]:
        user = self.users.get(user_id)
        return user["role"] if user else None

    def get_tenant(self, user_id: str) -> Optional[str]:
        user = self.users.get(user_id)
        return user["tenant_id"] if user else None
