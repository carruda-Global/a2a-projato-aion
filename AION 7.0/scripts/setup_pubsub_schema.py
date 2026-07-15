"""
Cria schema Avro no Pub/Sub e associa ao tópico ecosystem-aion-webhook.

Uso:
    python scripts/setup_pubsub_schema.py
"""
import json
from pathlib import Path

PROJECT_ID = "global-engenharia-498823"
SCHEMA_ID = "aion-marketplace-schema"
TOPIC_ID = "ecosystem-aion-webhook"
SUBSCRIPTION_ID = "aion-webhook-sub"
PUSH_ENDPOINT = "https://engenheiro-producao-ai.onrender.com/google/webhook"

SCHEMA_PATH = Path(__file__).parent.parent / "offers" / "pubsub_schema.json"


def get_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    CLIENT_SECRET = Path(__file__).parent.parent.parent / (
        "client_secret_757085749411-t95chtg2tpui3hjov165lratnj3fb0fc"
        ".apps.googleusercontent.com.json"
    )
    TOKEN_PATH = Path.home() / ".aion" / "google_marketplace_token.json"
    SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            if creds.expired:
                creds.refresh(Request())
        except Exception:
            TOKEN_PATH.unlink()
            creds = None

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
        print("Abrindo navegador para autenticar...")
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

    return creds


def create_schema(client, project_path: str, schema_definition: str):
    from google.cloud import pubsub_v1
    from google.pubsub_v1.types import Schema

    schema_path = f"{project_path}/schemas/{SCHEMA_ID}"
    try:
        existing = client.get_schema(request={"name": schema_path})
        print(f"  Schema ja existe: {existing.name}")
        return existing
    except Exception:
        pass

    schema = client.create_schema(
        request={
            "parent": project_path,
            "schema": Schema(
                name=schema_path,
                type_=Schema.Type.AVRO,
                definition=schema_definition,
            ),
            "schema_id": SCHEMA_ID,
        }
    )
    print(f"  Schema criado: {schema.name}")
    return schema


def create_topic_with_schema(publisher, project_path: str, schema_path: str):
    from google.cloud.pubsub_v1.types import SchemaSettings
    from google.pubsub_v1.types import Encoding

    topic_path = f"{project_path}/topics/{TOPIC_ID}"
    try:
        existing = publisher.get_topic(request={"topic": topic_path})
        print(f"  Topico ja existe: {existing.name}")
        return existing
    except Exception:
        pass

    topic = publisher.create_topic(
        request={
            "name": topic_path,
            "schema_settings": {
                "schema": schema_path,
                "encoding": "JSON",
            },
        }
    )
    print(f"  Topico criado com schema: {topic.name}")
    return topic


def create_push_subscription(subscriber, project_path: str):
    from google.pubsub_v1.types import PushConfig

    topic_path = f"{project_path}/topics/{TOPIC_ID}"
    sub_path = f"{project_path}/subscriptions/{SUBSCRIPTION_ID}"

    try:
        existing = subscriber.get_subscription(request={"subscription": sub_path})
        print(f"  Subscription ja existe: {existing.name}")
        return existing
    except Exception:
        pass

    sub = subscriber.create_subscription(
        request={
            "name": sub_path,
            "topic": topic_path,
            "push_config": PushConfig(push_endpoint=PUSH_ENDPOINT),
            "ack_deadline_seconds": 30,
        }
    )
    print(f"  Subscription criada: {sub.name}")
    print(f"  Push endpoint: {PUSH_ENDPOINT}")
    return sub


def main():
    print("=" * 60)
    print("  Pub/Sub Schema Setup - AION Marketplace")
    print(f"  Projeto: {PROJECT_ID}")
    print("=" * 60)

    try:
        from google.cloud import pubsub_v1
    except ImportError:
        print("Instalando google-cloud-pubsub...")
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-pubsub", "-q"])
        from google.cloud import pubsub_v1

    creds = get_credentials()
    schema_definition = SCHEMA_PATH.read_text(encoding="utf-8")
    project_path = f"projects/{PROJECT_ID}"

    schema_client = pubsub_v1.SchemaServiceClient(credentials=creds)
    publisher = pubsub_v1.PublisherClient(credentials=creds)
    subscriber = pubsub_v1.SubscriberClient(credentials=creds)

    print(f"\n[1/3] Schema Avro...")
    schema = create_schema(schema_client, project_path, schema_definition)
    schema_path = f"{project_path}/schemas/{SCHEMA_ID}"

    print(f"\n[2/3] Topico Pub/Sub com schema...")
    create_topic_with_schema(publisher, project_path, schema_path)

    print(f"\n[3/3] Push Subscription...")
    create_push_subscription(subscriber, project_path)

    print("\n" + "=" * 60)
    print("  Pub/Sub configurado!")
    print("=" * 60)
    print(f"\nSchema:       projects/{PROJECT_ID}/schemas/{SCHEMA_ID}")
    print(f"Topico:       projects/{PROJECT_ID}/topics/{TOPIC_ID}")
    print(f"Subscription: projects/{PROJECT_ID}/subscriptions/{SUBSCRIPTION_ID}")
    print(f"Push:         {PUSH_ENDPOINT}")
    print(f"\nValidacao de mensagens ATIVA (Avro)")
    print(f"Campos obrigatorios: eventType, entitlementId, customerId, timestamp")


if __name__ == "__main__":
    main()
