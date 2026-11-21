import re
from copy import deepcopy


def clean_text(value):

    if value is None:
        return None

    value = str(value)

    # Remove unnecessary whitespace
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_product(product):

    cleaned = deepcopy(product)

    # Clean text fields
    text_fields = [
        "product_id",
        "product_code",
        "product_name",
        "product_url",
        "currency",
        "discount",
        "availability"
    ]

    for field in text_fields:
        cleaned[field] = clean_text(cleaned.get(field))

    # Standardise prices
    price_fields = [
        "original_price",
        "current_price"
    ]

    for field in price_fields:

        value = cleaned.get(field)

        if value is not None:
            cleaned[field] = round(float(value), 2)

    return cleaned