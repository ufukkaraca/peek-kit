import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def retry_ax_call(retries=3, backoff=0.3):
    """
    A decorator to retry Accessibility API calls that may transiently fail
    with errors like kAXErrorCannotComplete when apps are animating.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # In pyobjc/atomacos, some errors map to exceptions.
                    # We catch general exceptions and retry if they look like AX errors.
                    err_str = str(e)
                    if "CannotComplete" in err_str or "InvalidUIElement" in err_str or "kAXError" in err_str:
                        last_err = e
                        logger.debug(f"AX call failed (attempt {attempt+1}/{retries}): {e}. Retrying...")
                        time.sleep(backoff)
                    else:
                        raise e
            raise last_err or Exception(f"AX call failed after {retries} retries")
        return wrapper
    return decorator
