from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request

from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.exceptions import install_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.models.loader import ModelManager

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = ModelManager(settings.model_uris)
    app.state.model_manager = manager
    manager.load_all()
    yield
    manager.clear()


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Centralized, versioned inference API for the project's MLflow models.",
        lifespan=lifespan,
    )

    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed",
                extra={"method": request.method, "path": request.url.path, "status_code": 500},
            )
            raise
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            },
        )
        return response

    install_exception_handlers(application)
    application.include_router(api_v1_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
