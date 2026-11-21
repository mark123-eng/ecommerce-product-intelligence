
import pytest

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from scrapers.perfume_scraper import PerfumeScraper


@pytest.fixture
def scraper():
    instance = PerfumeScraper()
    yield instance
    instance.close()


def test_perfume_scraper_inherits_base_scraper(scraper):
    assert isinstance(scraper, BaseScraper)


def test_parse_number(scraper):
    result = scraper.parse_number("1 250")

    assert result == 1250


def test_fetch_soup_returns_beautiful_soup(scraper, monkeypatch):
    html = """
    <html>
        <body>
            <h1>Perfume Products</h1>
        </body>
    </html>
    """

    # Mock the BaseScraper method because fetch_soup()
    # explicitly calls super().fetch_page().
    monkeypatch.setattr(
        BaseScraper,
        "fetch_page",
        lambda self, url: html
    )

    soup = scraper.fetch_soup(
        "https://example.com/products"
    )

    assert isinstance(soup, BeautifulSoup)
    assert soup.find("h1").text == "Perfume Products"


def test_extract_products_returns_expected_fields(scraper):
    html = """
    <ul>
        <li class="cs-product-gallery__item">
            <a class="cs-goods-title"
               href="/ua/product-1">
                Test Perfume
            </a>

            <div class="cs-goods-price">
                1250 грн
            </div>
        </li>
    </ul>
    """

    soup = BeautifulSoup(html, "html.parser")

    products = scraper.extract_products(
        soup,
        "Original Packaging"
    )

    assert len(products) == 1

    product = products[0]

    expected_fields = {
        "product_name",
        "current_price",
        "original_price",
        "currency",
        "product_url",
        "source",
        "category",
    }

    assert expected_fields.issubset(product.keys())
    assert product["product_name"] == "Test Perfume"
    assert product["category"] == "Original Packaging"


def test_duplicate_products_are_not_extracted_twice(scraper):
    html = """
    <ul>
        <li class="cs-product-gallery__item">
            <a class="cs-goods-title"
               href="/ua/product-1">
                Test Perfume
            </a>

            <div class="cs-goods-price">
                1250 грн
            </div>
        </li>
    </ul>
    """

    soup = BeautifulSoup(html, "html.parser")

    first_result = scraper.extract_products(
        soup,
        "Original Packaging"
    )

    second_result = scraper.extract_products(
        soup,
        "Original Packaging"
    )

    assert len(first_result) == 1
    assert len(second_result) == 0


def test_find_next_page_returns_correct_url(scraper):
    html = """
    <html>
        <body>
            <a rel="next" href="/ua/products/page_2">
                Next
            </a>
        </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")

    result = scraper.find_next_page(
        soup,
        "https://tomkardy.com.ua/ua/products"
    )

    assert result == (
        "https://tomkardy.com.ua/ua/products/page_2"
    )


def test_find_next_page_returns_none_when_missing(scraper):
    html = """
    <html>
        <body>
            <h1>Products</h1>
        </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")

    result = scraper.find_next_page(
        soup,
        "https://tomkardy.com.ua/ua/products"
    )

    assert result is None


def test_robots_disallowed_page_is_not_requested(
    scraper,
    monkeypatch
):
    monkeypatch.setattr(
        scraper,
        "check_permission",
        lambda url: False
    )

    def unexpected_request(*args, **kwargs):
        pytest.fail(
            "A disallowed page should not be requested"
        )

    monkeypatch.setattr(
        scraper.session,
        "get",
        unexpected_request
    )

    result = scraper.fetch_page(
        "https://tomkardy.com.ua/ua/products"
    )

    assert result is None
