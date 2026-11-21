import pytest
import requests

from unittest.mock import Mock

from scrapers.base_scraper import BaseScraper


@pytest.fixture
def scraper():
    """
    Create a BaseScraper instance for each test.
    """

    return BaseScraper()


def test_successful_page_request(scraper):

    mock_response = Mock()

    mock_response.text = (
        "<html><body>Test Page</body></html>"
    )

    mock_response.headers = {
        "Content-Type": "text/html; charset=UTF-8"
    }

    mock_response.raise_for_status.return_value = None

    scraper.session.get = Mock(
        return_value=mock_response
    )

    result = scraper.fetch_page(
        "https://example.com"
    )

    assert result == (
        "<html><body>Test Page</body></html>"
    )

    scraper.session.get.assert_called_once_with(
        "https://example.com",
        timeout=20
    )


def test_request_timeout(scraper):

    scraper.session.get = Mock(
        side_effect=requests.exceptions.Timeout
    )

    with pytest.raises(
        requests.exceptions.Timeout
    ):

        scraper.fetch_page(
            "https://example.com"
        )


def test_connection_error(scraper):

    scraper.session.get = Mock(
        side_effect=requests.exceptions.ConnectionError
    )

    with pytest.raises(
        requests.exceptions.ConnectionError
    ):

        scraper.fetch_page(
            "https://example.com"
        )


def test_http_error(scraper):

    mock_response = Mock()

    mock_response.status_code = 403

    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError(
            response=mock_response
        )
    )

    scraper.session.get = Mock(
        return_value=mock_response
    )

    with pytest.raises(
        requests.exceptions.HTTPError
    ):

        scraper.fetch_page(
            "https://example.com"
        )


def test_unexpected_content_type(scraper):

    mock_response = Mock()

    mock_response.text = "Not HTML"

    mock_response.headers = {
        "Content-Type": "application/json"
    }

    mock_response.raise_for_status.return_value = None

    scraper.session.get = Mock(
        return_value=mock_response
    )

    with pytest.raises(ValueError):

        scraper.fetch_page(
            "https://example.com"
        )


def test_session_closes(scraper):

    scraper.session.close = Mock()

    scraper.close()

    scraper.session.close.assert_called_once()