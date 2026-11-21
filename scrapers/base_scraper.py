import time
import requests

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from requests.exceptions import (
    HTTPError,
    Timeout,
    ConnectionError,
    RequestException
)

from config.logging_config import setup_logging


logger = setup_logging()


class RobotsPermissionError(RuntimeError):
    """Raised when robots.txt permissions cannot be verified."""


class BaseScraper:
    """
    Reusable base scraper responsible for:

    - HTTP sessions
    - Request handling
    - Timeouts
    - Robots.txt compliance
    - Request rate limiting
    - HTML validation
    - Session cleanup
    """

    def __init__(
        self,
        timeout=20,
        user_agent="EcommerceProductIntelligence/1.0",
        respect_robots_txt=False,
        request_delay=0
    ):

        self.timeout = timeout
        self.user_agent = user_agent
        self.respect_robots_txt = respect_robots_txt
        self.request_delay = max(0, request_delay)

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": self.user_agent
        })

        self.robots_cache = {}

        self.last_request_time = None

        logger.info("Base scraper initialized.")

    def _apply_request_delay(self):
        """
        Enforce a minimum delay between HTTP requests.
        """

        if self.last_request_time is not None:

            elapsed = (
                time.monotonic() - self.last_request_time
            )

            remaining = self.request_delay - elapsed

            if remaining > 0:
                time.sleep(remaining)

    def _make_request(self, url):
        """
        Perform a rate-limited HTTP GET request.
        """

        self._apply_request_delay()

        try:

            response = self.session.get(
                url,
                timeout=self.timeout
            )

            self.last_request_time = time.monotonic()

            return response

        except RequestException:

            self.last_request_time = time.monotonic()

            raise

    @staticmethod
    def _validate_robots_response(response, robots_url):
        """
        Validate that a response contains robots.txt content
        rather than an HTML error or CAPTCHA page.
        """

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        body = response.text.strip().lower()

        if "text/html" in content_type:

            raise RobotsPermissionError(
                f"robots.txt returned HTML instead of "
                f"robots directives: {robots_url}"
            )

        html_indicators = (
            "<!doctype html",
            "<html",
            "<head",
            "<body",
            "<form",
            "recaptcha",
            "bot protection"
        )

        if any(
            indicator in body
            for indicator in html_indicators
        ):

            raise RobotsPermissionError(
                f"robots.txt contains an HTML or bot-protection "
                f"response: {robots_url}"
            )

    def check_permission(self, url):
        """
        Check whether robots.txt permits accessing a URL.

        Robots rules are cached by website origin.

        Permission verification fails closed when robots.txt
        cannot be retrieved or validated.
        """

        parsed_url = urlparse(url)

        if (
            parsed_url.scheme not in ("http", "https")
            or not parsed_url.netloc
        ):

            raise ValueError(
                f"Invalid HTTP URL: {url}"
            )

        origin = (
            f"{parsed_url.scheme}://{parsed_url.netloc}"
        )

        robots_url = f"{origin}/robots.txt"

        if origin not in self.robots_cache:

            parser = RobotFileParser()

            try:

                response = self._make_request(
                    robots_url
                )

                if response.status_code == 429:

                    retry_after = response.headers.get(
                        "Retry-After",
                        "Not specified"
                    )

                    raise RobotsPermissionError(
                        "Website rate-limited the robots.txt "
                        f"request. Retry-After: {retry_after}"
                    )

                response.raise_for_status()

                self._validate_robots_response(
                    response,
                    robots_url
                )

                parser.set_url(robots_url)

                parser.parse(
                    response.text.splitlines()
                )

                # Cache only after successful retrieval
                # and validation.
                self.robots_cache[origin] = parser

                logger.info(
                    "Successfully retrieved and validated "
                    "robots.txt: %s",
                    robots_url
                )

            except RobotsPermissionError:

                logger.error(
                    "Robots permission verification failed: %s",
                    robots_url
                )

                raise

            except RequestException as error:

                logger.exception(
                    "Unable to retrieve robots.txt: %s",
                    robots_url
                )

                raise RobotsPermissionError(
                    f"Could not verify crawling permissions: {error}"
                ) from error

        allowed = self.robots_cache[origin].can_fetch(
            self.user_agent,
            url
        )

        if not allowed:

            logger.warning(
                "Robots.txt disallows access: %s",
                url
            )

        return allowed

    def fetch_page(self, url):
        """
        Retrieve HTML content from a webpage.

        Returns:
            str: HTML document.

            None: When robots.txt disallows access.

        Raises:
            RobotsPermissionError: When permission cannot
            be verified.
        """

        logger.info(
            "Requesting webpage: %s",
            url
        )

        if self.respect_robots_txt:

            if not self.check_permission(url):

                logger.warning(
                    "Skipping disallowed URL: %s",
                    url
                )

                return None

        try:

            response = self._make_request(url)

            if response.status_code == 429:

                retry_after = response.headers.get(
                    "Retry-After",
                    "Not specified"
                )

                logger.warning(
                    "HTTP 429 received. Retry-After: %s",
                    retry_after
                )

                raise HTTPError(
                    "Website rate-limited the request.",
                    response=response
                )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            if "text/html" not in content_type.lower():

                logger.warning(
                    "Unexpected content type: %s",
                    content_type
                )

                raise ValueError(
                    f"Expected HTML but received: {content_type}"
                )

            logger.info(
                "Successfully retrieved webpage: %s",
                url
            )

            return response.text

        except Timeout:

            logger.exception(
                "Request timed out: %s",
                url
            )

            raise

        except ConnectionError:

            logger.exception(
                "Connection failed: %s",
                url
            )

            raise

        except HTTPError as error:

            status_code = (
                error.response.status_code
                if error.response is not None
                else "Unknown"
            )

            logger.error(
                "HTTP request failed. Status: %s, URL: %s",
                status_code,
                url
            )

            raise

        except RequestException:

            logger.exception(
                "Unexpected request error: %s",
                url
            )

            raise

    def close(self):
        """
        Close the HTTP session.
        """

        self.session.close()

        logger.info(
            "HTTP session closed."
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
