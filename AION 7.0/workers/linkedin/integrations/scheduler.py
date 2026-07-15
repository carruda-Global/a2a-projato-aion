import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from .config import LinkedInConfig
from .oauth import LinkedInOAuth
from .tools import LinkedInTools

logger = logging.getLogger(__name__)


class ScheduledPost:
    def __init__(self, post_id: str, text: str, schedule_at: datetime, link_url: str | None = None):
        self.post_id = post_id
        self.text = text
        self.schedule_at = schedule_at
        self.link_url = link_url
        self.published: bool = False
        self.published_at: datetime | None = None
        self.error: str | None = None

    def to_dict(self) -> dict:
        return {
            "post_id": self.post_id,
            "text": self.text[:100],
            "schedule_at": self.schedule_at.isoformat(),
            "link_url": self.link_url,
            "published": self.published,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "error": self.error,
        }


class LinkedInScheduler:
    def __init__(self, config: LinkedInConfig, oauth: LinkedInOAuth):
        self.config = config
        self.oauth = oauth
        self.tools = LinkedInTools(config, oauth)
        self._scheduled: list[ScheduledPost] = []
        self._running = False
        self._task: asyncio.Task | None = None
        self._storage_path = config.token_storage_path / "scheduled_posts.json"

    def _load_scheduled(self):
        if self._storage_path.exists():
            try:
                data = json.loads(self._storage_path.read_text())
                for item in data:
                    post = ScheduledPost(
                        post_id=item.get("post_id", ""),
                        text=item.get("text", ""),
                        schedule_at=datetime.fromisoformat(item["schedule_at"]),
                        link_url=item.get("link_url"),
                    )
                    post.published = item.get("published", False)
                    if item.get("published_at"):
                        post.published_at = datetime.fromisoformat(item["published_at"])
                    post.error = item.get("error")
                    self._scheduled.append(post)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load scheduled posts: {e}")

    def _save_scheduled(self):
        data = [p.to_dict() for p in self._scheduled]
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def schedule_post(self, text: str, schedule_at: datetime, link_url: str | None = None) -> str:
        post_id = f"scheduled_{len(self._scheduled) + 1}_{int(datetime.now().timestamp())}"
        post = ScheduledPost(post_id=post_id, text=text, schedule_at=schedule_at, link_url=link_url)
        self._scheduled.append(post)
        self._save_scheduled()
        logger.info(f"Post scheduled: {post_id} at {schedule_at.isoformat()}")
        return post_id

    def list_scheduled(self, include_published: bool = False) -> list[dict]:
        posts = self._scheduled if include_published else [p for p in self._scheduled if not p.published]
        return [p.to_dict() for p in posts]

    def cancel_scheduled(self, post_id: str) -> bool:
        for i, post in enumerate(self._scheduled):
            if post.post_id == post_id and not post.published:
                self._scheduled.pop(i)
                self._save_scheduled()
                return True
        return False

    async def _check_and_publish(self):
        now = datetime.now()
        for post in self._scheduled:
            if post.published:
                continue
            if post.schedule_at <= now:
                try:
                    result = await self.tools.create_post(
                        text=post.text,
                        link_url=post.link_url,
                    )
                    if "error" in result:
                        post.error = str(result["error"])
                        logger.error(f"Failed to publish {post.post_id}: {result['error']}")
                    else:
                        post.published = True
                        post.published_at = datetime.now()
                        logger.info(f"Scheduled post published: {post.post_id}")
                except Exception as e:
                    post.error = str(e)
                    logger.exception(f"Error publishing scheduled post {post.post_id}")
        self._save_scheduled()

    async def _run_loop(self):
        logger.info("LinkedIn scheduler loop started")
        while self._running:
            try:
                await self._check_and_publish()
            except Exception as e:
                logger.exception(f"Scheduler error: {e}")
            await asyncio.sleep(self.config.scheduler_check_interval)

    async def start(self):
        if self._running:
            return
        self._running = True
        self._load_scheduled()
        self._task = asyncio.create_task(self._run_loop())
        logger.info("LinkedIn scheduler started")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._save_scheduled()
        logger.info("LinkedIn scheduler stopped")
