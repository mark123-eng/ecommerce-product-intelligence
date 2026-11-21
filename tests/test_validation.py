from processors.validation import validate_product, is_valid_product


def test_valid_product():

    product = {
        "product_id": "2865058172",
        "product_name": "Amouage Existence 100 ml",
        "product_url": "https://tomkardy.com.ua/product",
        "original_price": 2030.0,
        "current_price": 1750.0,
        "currency": "UAH"
    }

    assert is_valid_product(product) is True

    assert validate_product(product) == []


def test_invalid_product():

    product = {
        "product_id": "",
        "product_name": "",
        "product_url": "invalid-url",
        "original_price": 1000.0,
        "current_price": 1500.0,
        "currency": "UAH"
    }

    errors = validate_product(product)

    assert len(errors) > 0

    assert is_valid_product(product) is False