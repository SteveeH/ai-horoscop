import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.config import DB_NAMES, SERVER_SETTINGS
from app.routers import api_router, status_router
from app.utils.database import DB

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Server settings:")
    logger.info(SERVER_SETTINGS.model_dump_json(indent=2))

    logger.info("Database collection names:")
    logger.info(DB_NAMES.model_dump_json(indent=2))

    # Yield control to the application
    logger.info("Application is starting up...")
    yield
    logger.info("Application is shutting down...")

    # Shutdown
    logger.info("MongoDB connection closed")
    DB.close_connection()


app = FastAPI(
    title=SERVER_SETTINGS.SERVER_TITLE,
    description=SERVER_SETTINGS.SERVER_DESCRIPTION,
    version=SERVER_SETTINGS.SERVER_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SERVER_SETTINGS.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the API routers
app.include_router(status_router)
app.include_router(api_router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=SERVER_SETTINGS.APP_HOST,
        port=SERVER_SETTINGS.APP_PORT,
        reload=SERVER_SETTINGS.APP_DEBUG,
    )
