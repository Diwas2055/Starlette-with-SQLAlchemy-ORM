import asyncio
import logging
import os
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from queue import Queue  # Using sync Queue as QueueListener works with this

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


# Set up logging
logging.basicConfig(level=logging.NOTSET)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# Define a function to set up a TimedRotatingFileHandler
def create_timed_rotating_handler(
    log_file, level, formatter, when="midnight", backup_count=7
):
    handler = TimedRotatingFileHandler(
        filename=log_file, when=when, backupCount=backup_count
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler.addFilter(SeverityFilter(level))
    return handler


# Helper coroutine to setup and manage the logger
async def init_logger():
    # Create handlers for each level using the reusable function
    info_handler = create_timed_rotating_handler(info_log_file, logging.INFO, formatter)
    warning_handler = create_timed_rotating_handler(
        warning_log_file, logging.WARNING, formatter
    )
    error_handler = create_timed_rotating_handler(
        error_log_file, logging.ERROR, formatter
    )

    # Create a Queue for log records
    log_queue = Queue()

    # Set up QueueHandler
    queue_handler = QueueHandler(log_queue)

    # Add the QueueHandler to the logger
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)  # Ensure logger captures all levels
    logger.handlers = []  # Clear any existing handlers to avoid duplicates
    logger.addHandler(queue_handler)

    # Set up QueueListener with the actual handlers
    listener = QueueListener(log_queue, info_handler, warning_handler, error_handler)

    # Add StreamHandler for console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Set to DEBUG for console
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        # Start the listener
        listener.start()
        # Report the logger is ready
        logging.debug("Logger has started")
        # Wait forever to keep the logger running
        while True:
            await asyncio.sleep(60)
    finally:
        # Report the logger is done
        logging.debug("Logger is shutting down")
        # Ensure the listener is closed
        listener.stop()


# Initialize the logger
log_task = asyncio.create_task(init_logger())
logger = logging.getLogger()
