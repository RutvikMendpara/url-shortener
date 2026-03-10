from fastapi import FastAPI
from app.api.routes.url import router as url_router

app = FastAPI()

app.include_router(url_router)

@app.get("/")
def health_check():
    return {"status": "running"}

