import logging
from collections.abc import Collection

import click

from simple_http_checker.checker import check_urls

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@click.command()
@click.argument("urls", nargs=-1)
@click.option("--timeout", default=5, help="Timeout in seconds for each request.")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
def main(urls: Collection[str], timeout: int, verbose: bool):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    logger.debug(f"Received urls: {urls}")
    logger.debug(f"Received timeout: {timeout}")
    logger.debug(f"Received verbose: {verbose}")

    if not urls:
        logger.error("No URLs provided.")
        click.echo("Usage: check-urls <url1> <url2> ...")
        return

    results = check_urls(urls, timeout)

    click.echo("\n --- Results ---")
    for url, status in results.items():
        if status.endswith("OK"):
            fg_color = "green"
        else:
            fg_color = "red"
        click.secho(f"{url:<40} -> {status}", fg=fg_color)
