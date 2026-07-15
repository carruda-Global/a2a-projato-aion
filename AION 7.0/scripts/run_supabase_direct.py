import asyncio, asyncpg, os
from pathlib import Path

async def main():
    sql_path = Path(__file__).parent / "init-db.sql"
    sql = sql_path.read_text(encoding="utf-8")

    pg_url = os.environ.get("PG_DIRECT_URL")
    if not pg_url:
        print("Erro: Defina PG_DIRECT_URL no .env")
        return

    print("Conectando ao PostgreSQL via SSL...")
    try:
        conn = await asyncpg.connect(pg_url, ssl="require")
        print("Conectado! Executando SQL...")
        await conn.execute(sql)
        print("SQL executado com sucesso! Tabelas criadas.")
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        )
        print("Tabelas no schema public:", [t["table_name"] for t in tables])
        await conn.close()
    except Exception as e:
        print(f"Erro: {e}")

asyncio.run(main())
