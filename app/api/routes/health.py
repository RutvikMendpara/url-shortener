from fastapi import APIRouter, Response, status
from app.db.database import engine
from app.db.redis import redis_client
from sqlalchemy import text

router = APIRouter()
@router.get("/health", tags=["system"])
def health_check():
    postgres_ok = True
    redis_ok = True

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        postgres_ok = False
        print("Postgres error:", e)

    try:
        redis_client.ping()
    except Exception as e:
        redis_ok = False
        print("Redis error:", e)

    return {
        "status": "ok" if postgres_ok and redis_ok else "unhealthy",
        "postgres": postgres_ok,
        "redis": redis_ok
    }