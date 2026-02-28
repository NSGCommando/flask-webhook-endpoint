"""
project_logger.py

This module configures a project-wide logger named 'webhook_logger'.
It writes logs to 'logs/eventLogs.log' and also outputs to the console.
Usage:
    from app.project_logger import project_logger
    project_logger.info("Some message")
"""
import logging
import os

# Ensure the logs folder exists
os.makedirs("logs", exist_ok=True)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/eventLogs.log"),
        logging.StreamHandler()  # logs also to console
    ]
)

project_logger = logging.getLogger("webhook_logger")