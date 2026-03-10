from fastapi import APIRouter, Depends , HTTPException , status
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app.db.deps import get_db
from app.models.url import URL
from app.api.schemas.url import URLCreate, URLResponse
from app.services.short_code import encode_base62

router = APIRouter()

@router.post("/shorten", response_model=URLResponse)
def create_short_url(payload: URLCreate, db: Session = Depends(get_db)):

    # Step 1: create row
    url = URL(
       original_url=str(payload.original_url),
    expires_at=payload.expires_at
    )

    db.add(url)
    db.commit()
    db.refresh(url)


    # Step 2: generate short code
    short_code = encode_base62(url.id)

    # Step 3: update row with short code
    url.short_code = short_code
    db.commit()

    
    return {
        "short_url": f"http://localhost:8000/{short_code}"
    }



@router.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):

    url = db.query(URL).filter(URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return RedirectResponse(url.original_url)