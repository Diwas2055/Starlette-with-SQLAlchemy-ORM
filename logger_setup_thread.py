import logging
from logging.handlers import TimedRotatingFileHandler
import os
import concurrent.futures

log_folder = "logs"
info_log_file = os.path.join(log_folder, "info/info.log")
warning_log_file = os.path.join(log_folder, "warning/warning.log")
error_log_file = os.path.join(log_folder, "error/error.log")

logs_files = [info_log_file, warning_log_file, error_log_file]

# Check if the log files exist and create them if they don't exist
for log_file in logs_files:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            pass


# Custom filter to filter log records based on severity level
class SeverityFilter(logging.Filter):
    def __init__(self, severity):
        super().__init__()
        self.severity = severity

    def filter(self, record):
        return record.levelno == self.severity


# Asynchronous handler wrapper to use ThreadPoolExecutor
class AsyncHandler(logging.Handler):
    def __init__(self, handler, executor):
        super().__init__()
        self.handler = handler
        self.executor = executor

    def emit(self, record):
        # Offload the logging task to a thread pool
        self.executor.submit(self.handler.emit, record)


# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a ThreadPoolExecutor for non-blocking logging
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)


# Function to create and return TimedRotatingFileHandler for a specific level
def create_handler(log_file, level, formatter):
    handler = TimedRotatingFileHandler(
        filename=log_file, when="midnight", backupCount=7
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler.addFilter(SeverityFilter(level))
    return handler


# Create handlers for each log level
info_handler = create_handler(info_log_file, logging.INFO, formatter)
warning_handler = create_handler(warning_log_file, logging.WARNING, formatter)
error_handler = create_handler(error_log_file, logging.ERROR, formatter)

# Wrap the handlers with the AsyncHandler
async_info_handler = AsyncHandler(info_handler, executor)
async_warning_handler = AsyncHandler(warning_handler, executor)
async_error_handler = AsyncHandler(error_handler, executor)

# Remove all existing handlers to avoid duplication
logger = logging.getLogger()
logger.handlers = []  # Clear existing handlers

# Add asynchronous handlers to the logger
logger.addHandler(async_info_handler)
logger.addHandler(async_warning_handler)
logger.addHandler(async_error_handler)

# Set logging level for the logger
logger.setLevel(logging.NOTSET)

# Example log calls
logger.info("Info log message")
logger.warning("Warning log message")
logger.error("Error log message")
