import json
import logging
import os
from datetime import datetime, timezone

from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None

CLUSTER_TO_TOPIC = {
    "aec_core": "aec.tasks",
    "aec_specialized": "aec.tasks",
    "aec_compliance": "aec.tasks",
    "regulatory": "regulatory.tasks",
    "microsoft": "microsoft.tasks",
    "cross_sell": "cross_sell.tasks",
}


async def init_producer() -> None:
    global _producer
    kafka_url = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
    if not kafka_url:
        logger.warning("KAFKA_BOOTSTRAP_SERVERS nao configurada — Kafka desabilitado")
        _producer = None
        return
    _producer = AIOKafkaProducer(
        bootstrap_servers=kafka_url,
        value_serializer=lambda v: json.dumps(v).encode(),
        key_serializer=lambda k: k.encode() if k else None,
    )
    await _producer.start()
    logger.info("Kafka producer iniciado: %s", kafka_url)


async def close_producer() -> None:
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None


async def enqueue_agent_task(
    task_id: str,
    tenant_id: str,
    agent_id: str,
    cluster: str,
    task_type: str,
    payload: dict,
) -> None:
    if not _producer:
        raise RuntimeError("Kafka producer nao inicializado")

    topic = CLUSTER_TO_TOPIC.get(cluster, "admin.tasks")
    message = {
        "task_id": task_id,
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "cluster": cluster,
        "task_type": task_type,
        "payload": payload,
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }
    await _producer.send_and_wait(topic, value=message, key=tenant_id)
    logger.info("Task enfileirada: task=%s agent=%s topic=%s", task_id, agent_id, topic)
