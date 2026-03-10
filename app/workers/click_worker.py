from app.db.database import SessionLocal
from app.models.url import URL


def process_click(short_code: str):
    db = SessionLocal()

    url = db.query(URL).filter(URL.short_code == short_code).first()

    if url:
        url.click_count += 1
        db.commit()

    db.close()