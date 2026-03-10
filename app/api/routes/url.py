from fastapi import APIRouter, Depends , HTTPException , status, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app.db.deps import get_db
from app.models.url import URL
from app.api.schemas.url import URLCreate, URLResponse , URLStatsResponse
from app.services.short_code import encode_base62
from app.db.redis import redis_client

from app.queue import queue
from app.workers.click_worker import process_click
from app.services.rate_limiter import is_rate_limited
from app.core.logging import logger
from app.core.metrics import redirect_requests, cache_hits, cache_misses, url_creations, rate_limited_requests


router = APIRouter(prefix="/url")

@router.post("/shorten", response_model=URLResponse)
def create_short_url(payload: URLCreate,   request: Request, db: Session = Depends(get_db)):

    ip = request.client.host

    if is_rate_limited(ip):
        rate_limited_requests.inc()
        logger.warning(
            "rate_limited",
            extra={"ip": ip}
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Step 1: create row
    url = URL(
       original_url=str(payload.original_url),
    expires_at=payload.expires_at
    )
    url_creations.inc()
    db.add(url)
    db.commit()
    db.refresh(url)


    # Step 2: generate short code
    short_code = encode_base62(url.id)

    # Step 3: update row with short code
    url.short_code = short_code
    db.commit()

    logger.info(
    "short_url_created",
    extra={
        "original_url": payload.original_url,
        "short_code": short_code,
        "ip": ip
    }
)

    return {
        "short_url": f"http://localhost:8000/url/{short_code}"
    }



@router.get("/stats/{short_code}", response_model=URLStatsResponse)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):

    url = db.query(URL).filter(URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {
        "short_code": url.short_code,
        "original_url": url.original_url,
        "click_count": url.click_count,
        "created_at": url.created_at,
        "expires_at": url.expires_at,
    }


@router.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):

    redirect_requests.inc()

    # 1. Check Redis cache
    cached_url = redis_client.get(short_code)

    if cached_url:
        cache_hits.inc()
        # print("Cache hit")
        url = db.query(URL).filter(URL.short_code == short_code).first()
        if url:
            queue.enqueue(process_click, short_code)
        logger.info(
            "redirect_request",
            extra={
                "short_code": short_code,
                "cache_hit": bool(cached_url)
            }
        )

        return RedirectResponse(cached_url)
    
    # 2. Fallback to database
    cache_misses.inc()
    url = db.query(URL).filter(URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")


    # 3. Store in Redis cache
    # print("Cache miss - storing in Redis")
    redis_client.set(short_code, url.original_url, ex=3600)  # Cache for 1 hour

    queue.enqueue(process_click, short_code)

    logger.info(
        "redirect_request",
        extra={
            "short_code": short_code,
            "cache_hit": bool(cached_url)
        }
    )

    return RedirectResponse(url.original_url)

