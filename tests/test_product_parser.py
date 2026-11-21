from pathlib import Path

from processors.product_parser import (
    extract_product,
    extract_products,
)


def test_product_extraction():

    html = Path(
        "data/raw/sample_product_card.html"
    ).read_text(encoding="utf-8")

    product = extract_product(html)

    assert product is not None
    assert product["product_id"] == "SYN-0001"
    assert product["product_code"] == "SYN-CODE-001"
    assert "Synthetic Eau de Parfum Example" in product["product_name"]
    assert product["original_price"] == 2030.0
    assert product["current_price"] == 1750.0


def test_missing_product_html():

    product = extract_product("<html><body></body></html>")

    assert product is None


def test_tester_product_extraction():

    html = Path(
        "data/raw/sample_tester_product_card.html"
    ).read_text(encoding="utf-8")

    product = extract_product(html)

    assert product is not None
    assert product["product_id"] == "SYN-TESTER-0001"
    assert product["product_code"] == "SYN-CODE-002"
    assert "Synthetic Tester Fragrance Example" in product["product_name"]
    assert product["original_price"] == 1230.0
    assert product["current_price"] == 1050.0
    assert product["currency"] == "UAH"


def test_extract_multiple_products():

    first_html = Path(
        "data/raw/sample_product_card.html"
    ).read_text(encoding="utf-8")

    second_html = Path(
        "data/raw/sample_tester_product_card.html"
    ).read_text(encoding="utf-8")

    products = extract_products(first_html + second_html)

    assert len(products) == 2

    product_ids = [
        product["product_id"]
        for product in products
    ]

    assert "SYN-0001" in product_ids
    assert "SYN-TESTER-0001" in product_ids


def test_extract_24_original_packaging_products():

    html = Path(
        "data/raw/original_packaging_multiple.html"
    ).read_text(encoding="utf-8")

    products = extract_products(html)

    assert len(products) == 24

    product_ids = [
        product["product_id"]
        for product in products
    ]

    assert all(product_ids)
    assert len(set(product_ids)) == 24


def test_extract_24_perfume_tester_products():

    html = Path(
        "data/raw/perfume_testers_multiple.html"
    ).read_text(encoding="utf-8")

    products = extract_products(html)

    assert len(products) == 24

    product_ids = [
        product["product_id"]
        for product in products
    ]

    assert all(product_ids)
    assert len(set(product_ids)) == 24