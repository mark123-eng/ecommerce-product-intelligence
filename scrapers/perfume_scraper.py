
import re

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from requests.exceptions import RequestException

from config.logging_config import setup_logging

from scrapers.base_scraper import BaseScraper


logger = setup_logging()


# =====================================================
# 1. PROJECT CONFIGURATION
# =====================================================

BASE_URL = "https://tomkardy.com.ua"

CATEGORY_URLS = {

    "original_packaging": (
        "https://tomkardy.com.ua/ua/"
        "g44619880-originalnaya-upakovka-oae"
    ),

    "testers": (
        "https://tomkardy.com.ua/ua/"
        "g35061078-tester-oae"
    )

}

REQUEST_DELAY = 3

REQUEST_TIMEOUT = 30

USER_AGENT = "EcommerceProductIntelligence/1.0"


# =====================================================
# 2. PERFUME SCRAPER
# =====================================================

class PerfumeScraper(BaseScraper):
    """
    Website-specific scraper for Tomkardy perfume products.

    Inherits from BaseScraper:

    - HTTP session management
    - Request timeout handling
    - robots.txt verification
    - Request rate limiting
    - HTTP error handling
    """

    def __init__(self):

        super().__init__(
            timeout=REQUEST_TIMEOUT,
            user_agent=USER_AGENT,
            respect_robots_txt=True,
            request_delay=REQUEST_DELAY
        )

        self.seen_products = set()

        logger.info(
            "Perfume scraper initialized."
        )

    # =================================================
    # 3. FETCH AND PARSE WEBPAGE
    # =================================================

    def fetch_soup(self, url):
        """
        Retrieve HTML through BaseScraper and convert
        it into a BeautifulSoup object.
        """

        try:

            html = super().fetch_page(url)

            if html is None:
                return None

            return BeautifulSoup(
                html,
                "html.parser"
            )

        except (
            RequestException,
            RuntimeError,
            ValueError
        ) as error:

            logger.error(
                "Could not retrieve or parse page %s: %s",
                url,
                error
            )

            return None

    # =================================================
    # 4. EXTRACT NUMERIC PRICE
    # =================================================

    @staticmethod
    def parse_number(text):
        """
        Extract numeric values from formatted price text.

        Examples:
            '1 250 грн' -> 1250.0
            '1,250.50'  -> 1250.50
            '850'       -> 850.0
        """

        if not text:
            return None

        match = re.search(
            r"\d[\d\s\u00a0]*(?:[.,]\d{1,2})?",
            text
        )

        if not match:
            return None

        number = match.group(0)

        number = number.replace(" ", "")
        number = number.replace("\u00a0", "")
        number = number.replace(",", ".")

        try:

            return float(number)

        except ValueError:

            return None

    # =================================================
    # 5. EXTRACT CURRENT AND ORIGINAL PRICES
    # =================================================

    def extract_price(self, price_element):
        """
        Extract current and original product prices.

        Original prices are identified using common
        old-price HTML selectors.
        """

        if price_element is None:
            return None, None

        old_price_selectors = [
            "del",
            "s",
            ".old-price",
            ".cs-goods-price-old"
        ]

        old_price_elements = []

        for selector in old_price_selectors:

            old_price_elements.extend(
                price_element.select(selector)
            )

        old_price_text = " ".join(
            element.get_text(" ", strip=True)
            for element in old_price_elements
        )

        old_price = self.parse_number(
            old_price_text
        )

        # Copy the HTML so the original soup is not modified.
        price_copy = BeautifulSoup(
            str(price_element),
            "html.parser"
        )

        copied_container = price_copy.select_one(
            ".cs-goods-price"
        )

        if copied_container is None:
            copied_container = price_copy

        # Remove old-price elements before extracting
        # the current price.
        for selector in old_price_selectors:

            for element in copied_container.select(selector):

                element.decompose()

        current_price_text = copied_container.get_text(
            " ",
            strip=True
        )

        current_price = self.parse_number(
            current_price_text
        )

        return current_price, old_price

    # =================================================
    # 6. EXTRACT INDIVIDUAL PRODUCTS
    # =================================================

    def extract_products(self, soup, category):
        """
        Extract product information from a category page.

        Returns a list of product dictionaries.
        """

        products = []

        product_cards = soup.select(
            "li.cs-product-gallery__item"
        )

        logger.info(
            "Found %s product cards in %s",
            len(product_cards),
            category
        )

        for card in product_cards:

            title_element = card.select_one(
                "a.cs-goods-title"
            )

            if title_element is None:
                continue

            product_name = title_element.get_text(
                " ",
                strip=True
            )

            product_url = title_element.get("href")

            if not product_url:
                continue

            product_url = urljoin(
                BASE_URL,
                product_url
            )

            if product_url in self.seen_products:
                continue

            self.seen_products.add(product_url)

            price_element = card.select_one(
                ".cs-goods-price"
            )

            current_price, original_price = (
                self.extract_price(price_element)
            )

            product = {

                "product_name": product_name,

                "current_price": current_price,

                "original_price": original_price,

                "currency": "UAH",

                "product_url": product_url,

                "source": BASE_URL,

                "category": category

            }

            products.append(product)

        return products

    # =================================================
    # 7. FIND NEXT PAGE
    # =================================================

    def find_next_page(self, soup, current_url):
        """
        Detect the next pagination URL.

        Rejects external domains and repeated current URLs.
        """

        possible_next_links = []

        possible_next_links.extend(
            soup.select('a[rel="next"]')
        )

        possible_next_links.extend(
            soup.select(
                "a.next, "
                "a.pagination-next, "
                ".pagination a.next"
            )
        )

        possible_next_links.extend(
            soup.select(
                'a[aria-label*="Next"], '
                'a[aria-label*="next"]'
            )
        )

        current_domain = urlparse(
            BASE_URL
        ).netloc

        for link in possible_next_links:

            href = link.get("href")

            if not href:
                continue

            next_url = urljoin(
                current_url,
                href
            )

            next_domain = urlparse(
                next_url
            ).netloc

            if next_domain != current_domain:
                continue

            if next_url == current_url:
                continue

            return next_url

        return None

    # =================================================
    # 8. SCRAPE CATEGORY HTML PAGES
    # =================================================

    def scrape_category_pages(self, category, start_url):
        """
        Fetch category pages and return their HTML.

        This method is designed for integration with
        processors.pipeline.process_category_pages().

        Returns:
            List[str]: Raw HTML page strings.
        """

        html_pages = []

        visited_pages = set()

        current_url = start_url

        while current_url:

            if current_url in visited_pages:

                logger.warning(
                    "Pagination loop detected: %s",
                    current_url
                )

                break

            visited_pages.add(current_url)

            print(
                f"\nScraping category: {category}"
            )

            print(
                f"Page: {current_url}"
            )

            soup = self.fetch_soup(
                current_url
            )

            if soup is None:

                print(
                    "Page could not be retrieved. "
                    "Stopping this category."
                )

                logger.warning(
                    "Stopping category %s because page retrieval failed.",
                    category
                )

                break

            # Preserve the fetched page as HTML.
            html_pages.append(
                str(soup)
            )

            print(
                f"HTML pages collected: {len(html_pages)}"
            )

            logger.info(
                "HTML page collected from %s",
                current_url
            )

            next_url = self.find_next_page(
                soup,
                current_url
            )

            current_url = next_url

        print(
            f"\nTotal HTML pages collected for "
            f"{category}: {len(html_pages)}"
        )

        logger.info(
            "Completed HTML collection for %s. Pages: %s",
            category,
            len(html_pages)
        )

        return html_pages

    # =================================================
    # 9. SCRAPE CATEGORY PRODUCTS
    # =================================================

    def scrape_category(self, category, start_url):
        """
        Fetch category pages and extract product dictionaries.

        Retained for direct product extraction and backward
        compatibility with the original scraper interface.
        """

        all_products = []

        visited_pages = set()

        current_url = start_url

        while current_url:

            if current_url in visited_pages:

                logger.warning(
                    "Pagination loop detected: %s",
                    current_url
                )

                break

            visited_pages.add(current_url)

            print(
                f"\nScraping category: {category}"
            )

            print(
                f"Page: {current_url}"
            )

            soup = self.fetch_soup(
                current_url
            )

            if soup is None:

                print(
                    "Page could not be retrieved. "
                    "Stopping this category."
                )

                break

            products = self.extract_products(
                soup,
                category
            )

            all_products.extend(
                products
            )

            print(
                f"Products extracted: {len(products)}"
            )

            logger.info(
                "%s products extracted from %s",
                len(products),
                current_url
            )

            next_url = self.find_next_page(
                soup,
                current_url
            )

            current_url = next_url

        print(
            f"\nTotal products in {category}: "
            f"{len(all_products)}"
        )

        logger.info(
            "Completed product extraction for %s. Products: %s",
            category,
            len(all_products)
        )

        return all_products
