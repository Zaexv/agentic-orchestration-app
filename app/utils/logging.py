"""Structured logging configuration for production."""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: str | None = None
) -> None:
    """
    Setup application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ("json" or "text")
        log_file: Optional log file path
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Set formatter
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Request logging middleware helper
def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str | None = None,
    **extra: Any
) -> None:
    """
    Log HTTP request with structured data.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user identifier
        **extra: Additional fields to log
    """
    logger = get_logger("api")
    
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    log_data.update(extra)
    
    logger.info(
        f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
        extra={"extra": log_data}
    )


def log_agent_execution(
    agent_name: str,
    user_query: str,
    confidence: float,
    duration_ms: float,
    success: bool = True,
    **extra: Any
) -> None:
    """
    Log agent execution with structured data.
    
    Args:
        agent_name: Name of the agent
        user_query: User's query
        confidence: Routing confidence score
        duration_ms: Execution duration
        success: Whether execution succeeded
        **extra: Additional fields
    """
    logger = get_logger("agents")
    
    log_data = {
        "agent": agent_name,
        "query_length": len(user_query),
        "confidence": round(confidence, 2),
        "duration_ms": round(duration_ms, 2),
        "success": success,
    }
    log_data.update(extra)
    
    logger.info(
        f"Agent execution: {agent_name} (confidence: {confidence:.2f})",
        extra={"extra": log_data}
    )
