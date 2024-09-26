import logging
from logging.handlers import TimedRotatingFileHandler
import os
import concurrent.futures
from functools import partial

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


# Set up logging
logging.basicConfig(level=logging.NOTSET)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a ThreadPoolExecutor for non-blocking logging
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

# Create a TimedRotatingFileHandler for each level and attach a filter
info_handler = TimedRotatingFileHandler(
    filename=info_log_file, when="midnight", backupCount=7
)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)
info_handler.addFilter(SeverityFilter(logging.INFO))

warning_handler = TimedRotatingFileHandler(
    filename=warning_log_file, when="midnight", backupCount=7
)
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(formatter)
warning_handler.addFilter(SeverityFilter(logging.WARNING))

error_handler = TimedRotatingFileHandler(
    filename=error_log_file, when="midnight", backupCount=7
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
error_handler.addFilter(SeverityFilter(logging.ERROR))

# Wrap the handlers with the AsyncHandler
async_info_handler = AsyncHandler(info_handler, executor)
async_warning_handler = AsyncHandler(warning_handler, executor)
async_error_handler = AsyncHandler(error_handler, executor)

# Create a logger and attach asynchronous handlers
logger = logging.getLogger()
logger.addHandler(async_info_handler)
logger.addHandler(async_warning_handler)
logger.addHandler(async_error_handler)
