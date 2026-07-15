import logging
from app.celery_app import celery_app
from app.services.storage import cleanup_expired

logger = logging.getLogger(__name__)

@celery_app.task(name='app.utils.cleanup.cleanup_expired_files')
def cleanup_expired_files():
    logger.info("Running periodic cleanup task")
    try:
        cleanup_expired()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)
