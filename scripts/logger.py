import logging
import os
import threading
import json
from datetime import datetime
from typing import Dict, Any, Optional

class GlobalLogger:
    """
    Thread-safe singleton logger with configurable backends
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Thread-safe singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GlobalLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger only once"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self._logger = None
        self._config_logger()
    
    def _config_logger(self):
        """Configure logger based on environment or default to file logging"""
        env = os.getenv("ENV", "default")
        self._setup_default_logger()
    
    def _setup_default_logger(self):
        """Default file-based logging"""
        self._logger = logging.getLogger("stock_pipeline")
        self._logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self._logger.handlers.clear()
        
        # File handler
        log_dir = "logs/scripts"
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(
            f"{log_dir}/script_logs.log", 
            mode='a', 
            encoding='utf-8'
        )
        file_handler.setFormatter(self._get_json_formatter())
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_simple_formatter())
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        self._logger.propagate = False
    
    def _get_json_formatter(self):
        """JSON formatter for structured logging"""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": record.levelname,
                    "module": record.name,
                    "message": record.getMessage(),
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Add extra fields if provided
                if hasattr(record, 'extra_data') and record.extra_data:
                    log_entry.update(record.extra_data)
                
                # Add exception info if present
                if record.exc_info:
                    log_entry['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry)
        
        return JSONFormatter()
    
    def _get_simple_formatter(self):
        """Simple formatter for console output"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def log_event(self, msg: str, level: str = "INFO", data: Optional[Dict[str, Any]] = None) -> None:
        """
        Thread-safe logging function
        
        Args:
            msg: Log message
            level: Log level (INFO, ERROR, DEBUG, WARNING, CRITICAL)
            data: Dictionary of additional fields to include in the log
        """
        if not self._logger:
            return
        
        import inspect
        
        # Get caller information
        frame = inspect.currentframe().f_back
        caller_module = frame.f_globals.get('__name__', 'unknown')
        caller_function = frame.f_code.co_name
        caller_line = frame.f_lineno
        
        # Create log record with extra data
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        with self._lock:
            # Create a custom LogRecord to include caller info and extra data
            record = self._logger.makeRecord(
                name=caller_module,
                level=log_level,
                fn=frame.f_code.co_filename,
                lno=caller_line,
                msg=msg,
                args=(),
                exc_info=None,
                func=caller_function
            )
            
            # Add extra data
            record.extra_data = data
            
            # Handle the record
            self._logger.handle(record)

# Create the singleton instance
logger = GlobalLogger()
