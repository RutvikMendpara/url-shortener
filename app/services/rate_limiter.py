from app.db.redis import redis_client


def is_rate_limited(ip: str, limit: int = 10, window: int = 60) -> bool:
    key = f"rate_limit:{ip}"
    current = redis_client.get(key)

    if current and int(current) >= limit:
        return True

    pipe = redis_client.pipeline()

    pipe.incr(key)

    if not current:
        pipe.expire(key, window)

    pipe.execute()

    return False