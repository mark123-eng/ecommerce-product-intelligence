from processors.cleaning import clean_product


def test_clean_product():

    product = {
        "product_id": "2865058172",
        "product_name": "  Amouage    Existence 100 ml. ",
        "product_url": " https://tomkardy.com.ua/product ",
        "original_price": 2030.0,
        "current_price": 1750.0,
        "currency": " UAH ",
        "discount": " –14% ",
        "availability": " Ready to ship "
    }

    cleaned = clean_product(product)

    assert cleaned["product_name"] == "Amouage Existence 100 ml."

    assert cleaned["currency"] == "UAH"

    assert cleaned["original_price"] == 2030.0

    assert cleaned["current_price"] == 1750.0