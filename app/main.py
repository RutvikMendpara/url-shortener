from fastapi import FastAPI, Response
from app.api.routes.url import router as url_router 
from app.api.routes.health import router as health_router
from app.middleware.metrics_middleware import MetricsMiddleware
from prometheus_client import generate_latest

app = FastAPI()

app.add_middleware(MetricsMiddleware)
app.include_router(url_router)
app.include_router(health_router)

@app.get("/")
def health_check():
    return {"status": "running"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")