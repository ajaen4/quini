import logging
import sys

# Configure the root logger
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout
)

# Get a logger for the current module
logger = logging.getLogger(__name__)
