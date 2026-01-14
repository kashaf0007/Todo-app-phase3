import logging
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from functools import wraps
import traceback
from typing import Callable, Any
import sys


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def setup_error_handlers(app):
    """Setup global error handlers for the FastAPI application"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred"},
        )


def log_function_call(func: Callable) -> Callable:
    """Decorator to log function calls and their results"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Calling function: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed with error: {str(e)}")
            raise

    return wrapper


def log_api_call(endpoint: str):
    """Decorator to log API endpoint calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"API call to {endpoint} started")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"API call to {endpoint} completed successfully")
                return result
            except Exception as e:
                logger.error(f"API call to {endpoint} failed with error: {str(e)}")
                raise

        return wrapper
    return decorator


def log_tool_call(tool_name: str):
    """Decorator to log MCP tool calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"MCP tool call: {tool_name} started")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"MCP tool call: {tool_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"MCP tool call: {tool_name} failed with error: {str(e)}")
                raise

        return wrapper
    return decorator


def log_db_operation(operation: str):
    """Decorator to log database operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"Database operation: {operation} started")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Database operation: {operation} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Database operation: {operation} failed with error: {str(e)}")
                raise

        return wrapper
    return decorator