from f_data_uploader.actions import run_data_uploader
from f_data_uploader.logger import logger


def handler(event, context):
    try:
        run_data_uploader()
    except Exception as e:
        logger.exception("Unhandled exception: %s", str(e))
        raise
