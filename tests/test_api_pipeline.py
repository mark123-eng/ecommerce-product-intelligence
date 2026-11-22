import pytest

from processors.pipeline import (
    process_api_products,
    process_and_store_api_products
)

from storage.database import (
    get_all_products
)

from scrapers.dummyjson_api import DummyJSONAPIClient


def sample_product(
    product_id=1,
    title="Essence Mascara Lash Princess",
    category="beauty",
    price=9.99
):

    return {
        "id": product_id,
        "title": title,
        "description": "Sample product description",
        "category": category,
        "price": price,
        "discountPercentage": 10.0,
        "rating": 4.5,
        "stock": 50,
        "sku": f"SKU-{product_id}",
        "availabilityStatus": "In Stock"
    }


def test_process_api_products():

    products = [
        sample_product()
    ]

    client = DummyJSONAPIClient()

    results = process_api_products(
        products,
        api_client=client
    )

    assert results["total_received"] == 1

    assert results["total_valid"] == 1

    assert results["total_invalid"] == 0

    assert results["duplicates_removed"] == 0

    product = results["valid_products"][0]

    assert product["product_id"] == "1"

    assert product["product_name"] == (
        "Essence Mascara Lash Princess"
    )

    assert product["category"] == "beauty"


def test_api_duplicate_detection():

    products = [
        sample_product(product_id=1),
        sample_product(product_id=1)
    ]

    client = DummyJSONAPIClient()

    results = process_api_products(
        products,
        api_client=client
    )

    assert results["total_received"] == 2

    assert results["total_valid"] == 1

    assert results["duplicates_removed"] == 1


def test_invalid_api_product():

    products = [
        sample_product(
            product_id=1,
            price="invalid"
        )
    ]

    client = DummyJSONAPIClient()

    results = process_api_products(
        products,
        api_client=client
    )

    assert results["total_received"] == 1

    assert results["total_valid"] == 0

    assert results["total_invalid"] == 1


def test_api_products_saved_to_database(tmp_path):

    db_path = tmp_path / "api_products.db"

    products = [
        sample_product(
            product_id=1,
            category="beauty"
        ),
        sample_product(
            product_id=2,
            title="Sample Fragrance",
            category="fragrances",
            price=25.50
        )
    ]

    client = DummyJSONAPIClient()

    results = process_and_store_api_products(
        api_products=products,
        db_path=db_path,
        api_client=client
    )

    saved_products = get_all_products(db_path)

    assert results["total_received"] == 2

    assert results["total_valid"] == 2

    assert results["saved_to_database"] == 2

    assert len(saved_products) == 2

    categories = {
        product["category"]
        for product in saved_products
    }

    assert categories == {
        "beauty",
        "fragrances"
    }

    sources = {
        product["source"]
        for product in saved_products
    }

    assert sources == {
        "dummyjson.com"
    }


def test_api_product_source_is_separate_from_html_source(
    tmp_path
):

    db_path = tmp_path / "multi_source.db"

    products = [
        sample_product(product_id=1)
    ]

    process_and_store_api_products(
        api_products=products,
        db_path=db_path
    )

    saved_products = get_all_products(db_path)

    assert saved_products[0]["source"] == "dummyjson.com"