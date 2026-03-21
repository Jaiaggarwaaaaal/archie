"""FastAPI entry point for Archie."""
from fastapi import FastAPI
from archie.api import routes
from archie.config import settings
import logging

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="Archie - AI Staff Engineer Agent", version="0.1.0")

app.include_router(routes.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Archie starting up...")
    logger.info("Initializing services...")
    routes.init_services()
    logger.info("Services initialized")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Archie shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
