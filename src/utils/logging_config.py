import logging
import os
from datetime import datetime

def setup_logging(log_file_prefix="app_log", log_dir=None):
    """
    Configures logging for the application.

    Args:
        log_file_prefix (str): Prefix for the log file name.
        log_dir (str, optional): Directory to save log files. Defaults to
                                 'src/data_collection/logs' relative to BASE_DIR.
    """
    if log_dir is None:
        # Determine BASE_DIR dynamically
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.abspath(os.path.join(current_file_dir, '..', '..', '..'))
        log_dir = os.path.join(base_dir, 'src', 'data_collection', 'logs')

    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"{log_file_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log")

    # Clear existing handlers to prevent duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    for handler in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler() # Also log to console
        ]
    )
    # Set a default logger for modules that just use logging.getLogger(__name__)
    # without specific handlers.
    logging.getLogger(__name__).addHandler(logging.NullHandler())

    # Configure StreamHandler for console with a concise format for specific loggers
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Apply console handler to specific loggers that need concise console output
    # For example, if you want 'src.data_collection.download_inventory' to have concise output
    # specific_logger = logging.getLogger('src.data_collection.download_inventory')
    # specific_logger.addHandler(console_handler)
    # specific_logger.propagate = False # Prevent propagation to root logger if full format is not desired
