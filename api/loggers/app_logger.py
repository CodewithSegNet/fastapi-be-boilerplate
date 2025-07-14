import logging

# Configure the logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d: %(message)s",
    handlers=[logging.FileHandler("logs/app_logs.log"), logging.StreamHandler()],
)

app_logger = logging.getLogger(__name__)
