import logging
from typing import Collection

import requests

logger = logging.getLogger(__name__)


def check_urls(urls: Collection[str], timeout: int = 5) -> dict[str, str]:
    """Checks a list of urls and returns their status.

    Args:
        urls (list[str]): A list of URLs to check.
        timeout (int, optional): The timeout in seconds for each URL check. Defaults to 5.

    Returns:
        dict[str, str]: A dictionary mapping URLs to their status.
    """

    logger.info(
        f"Starting check for {len(urls)} URLs with a timeout of {timeout} seconds."
    )

    results: dict[str, str] = {}
    for url in urls:
        status = "UNKNOWN"
        try:
            logger.debug(f"Checking URL: {url}")
            response = requests.get(url, timeout=timeout)

            if response.ok:
                status = f"{response.status_code} OK"
            else:
                status = f"{response.status_code} {response.reason}"
        except requests.exceptions.Timeout:
            status = "TIMEOUT"
        except requests.exceptions.ConnectionError:
            status = "CONNECTION_ERROR"
            logger.warning(f"Connection error for URL: {url}")
        except requests.exceptions.RequestException as e:
            status = f"REQUEST_ERROR: {type(e).__name__}"
            logger.error(
                f"An unexpected error occurred for {url}: {e}",
                exc_info=True,
            )

        results[url] = status
        logger.debug(f"Checked: {url:<40} -> {status}")

    logger.info("URL check complete")
    return results
