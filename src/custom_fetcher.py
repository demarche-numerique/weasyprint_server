from urllib.error import URLError
from weasyprint.urls import URLFetcher, FatalURLFetchingError
from .logger import ERROR_LOGGER


class CustomURLFetcher(URLFetcher):
    def fetch(self, url, headers=None):
        try:
            return super().fetch(url, headers)
        except URLError as e:
            ERROR_LOGGER.warning(
                "asset missing", exc_info=e, extra={"context": {"url": url}}
            )
            raise FatalURLFetchingError(f"Asset missing: {url}") from e
