from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import ingest, results, validation, health
from ..services.logger import get_logger

logger = get_logger()

app = FastAPI(title="my-content-processing-solution-accelerator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(ingest.router, prefix="/api/ingest")
app.include_router(results.router, prefix="/api/results")
app.include_router(validation.router, prefix="/api/validate")
app.include_router(health.router, prefix="/api/health")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code} for {request.url}")
        return response
    except Exception as e:
        logger.exception("Unhandled error")
        raise e


@app.get("/api/ready")
async def ready():
    return {"status": "ready"}
