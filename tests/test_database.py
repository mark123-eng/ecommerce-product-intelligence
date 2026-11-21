from storage.database import (
    initialize_database,
    save_products,
    get_all_products
)


def test_database_operations(tmp_path):

    db_path = tmp_path / "test_products.db"

    # Create database.
    initialize_database(db_path)

    products = [
        {
            "product_id": "2865058172",
            "product_code": "1358",
            "product_name": "Amouage Existence",
            "product_url": "https://tomkardy.com.ua/product1",
            "original_price": 2030.0,
            "current_price": 1750.0,
            "currency": "UAH",
            "discount": "-14%",
            "availability": "Ready to ship"
        }
    ]

    # Save product.
    saved = save_products(
        products,
        "Original Packaging",
        "https://tomkardy.com.ua/ua/g44619880-originalnaya-upakovka-oae",
        db_path
    )

    assert saved == 1

    # Retrieve products.
    stored_products = get_all_products(db_path)

    assert len(stored_products) == 1

    assert (
        stored_products[0]["product_id"]
        == "2865058172"
    )

    assert (
        stored_products[0]["current_price"]
        == 1750.0
    )

    assert (
        stored_products[0]["category"]
        == "Original Packaging"
    )


def test_database_prevents_duplicate_records(tmp_path):

    db_path = tmp_path / "duplicate_test.db"

    initialize_database(db_path)

    product = {
        "product_id": "2865058172",
        "product_code": "1358",
        "product_name": "Amouage Existence",
        "product_url": "https://tomkardy.com.ua/product1",
        "original_price": 2030.0,
        "current_price": 1750.0,
        "currency": "UAH",
        "discount": "-14%",
        "availability": "Ready to ship"
    }

    save_products(
        [product],
        "Original Packaging",
        "https://tomkardy.com.ua/category",
        db_path
    )

    # Change the price and save the same product again.
    updated_product = product.copy()

    updated_product["current_price"] = 950.0

    save_products(
        [updated_product],
        "Original Packaging",
        "https://tomkardy.com.ua/category",
        db_path
    )

    stored_products = get_all_products(db_path)

    assert len(stored_products) == 1

    assert stored_products[0]["current_price"] == 950.0