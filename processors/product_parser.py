from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BASE_URL = "https://tomkardy.com.ua"


def clean_price(price_text):
    """
    Converts a price such as '1 230 ₴' into 1230.0.
    """

    if not price_text:
        return None

    price_text = price_text.replace("\xa0", " ")

    numbers = re.sub(r"[^\d.]", "", price_text)

    if not numbers:
        return None

    return float(numbers)


def extract_product_from_card(card):
    """
    Extracts information from one product card.
    """

    title_element = card.select_one("a.cs-goods-title")

    product_name = (
        title_element.get_text(" ", strip=True)
        if title_element else None
    )

    product_url = None

    if title_element and title_element.get("href"):
        product_url = urljoin(BASE_URL, title_element["href"])

    button = card.select_one("button[data-product-id]")

    product_id = None
    original_price = None
    current_price = None

    if button:
        product_id = button.get("data-product-id")

        original_price = clean_price(
            button.get("data-product-price")
        )

        current_price = clean_price(
            button.get("data-product-discounted-price")
        )

    # Fallback to the product card's own ID if necessary.
    if not product_id:
        product_id = card.get("data-product-id")

    sku_element = card.select_one(
        ".cs-product-gallery__sku span"
    )

    product_code = (
        sku_element.get_text(" ", strip=True)
        if sku_element else None
    )

    discount_element = card.select_one(
        '[data-qaid="discount_label"]'
    )

    discount = (
        discount_element.get_text(" ", strip=True)
        if discount_element else None
    )

    availability_element = card.select_one(
        '[data-qaid="presence_data"]'
    )

    availability = (
        availability_element.get_text(" ", strip=True)
        if availability_element else None
    )

    return {
        "product_id": product_id,
        "product_code": product_code,
        "product_name": product_name,
        "product_url": product_url,
        "original_price": original_price,
        "current_price": current_price,
        "currency": "UAH",
        "discount": discount,
        "availability": availability
    }


def extract_product(product_html):
    """
    Extracts one product from a supplied HTML fragment.
    """

    soup = BeautifulSoup(product_html, "html.parser")

    card = soup.select_one("li.cs-product-gallery__item")

    if not card:
        return None

    return extract_product_from_card(card)


def extract_products(page_html):
    """
    Extracts all product cards from a category page.
    """

    soup = BeautifulSoup(page_html, "html.parser")

    product_cards = soup.select(
        "li.cs-product-gallery__item"
    )

    products = []

    for card in product_cards:
        product = extract_product_from_card(card)

        if product is not None:
            products.append(product)

    return products