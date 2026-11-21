from urllib.parse import urlparse


def validate_product(product):

    errors = []

    # Required fields
    required_fields = [
        "product_id",
        "product_name",
        "product_url",
        "current_price",
        "currency"
    ]

    for field in required_fields:

        if product.get(field) is None or product.get(field) == "":
            errors.append(f"Missing required field: {field}")

    # Validate product URL
    product_url = product.get("product_url")

    if product_url:

        parsed_url = urlparse(product_url)

        if parsed_url.scheme not in ("http", "https"):
            errors.append("Invalid URL scheme")

        if not parsed_url.netloc:
            errors.append("Invalid product URL")

    # Validate prices
    for field in ["original_price", "current_price"]:

        price = product.get(field)

        if price is not None:

            if not isinstance(price, (int, float)):
                errors.append(f"{field} must be numeric")

            elif price < 0:
                errors.append(f"{field} cannot be negative")

    # Check price consistency
    original = product.get("original_price")
    current = product.get("current_price")

    if original is not None and current is not None:

        if current > original:
            errors.append(
                "Current price cannot exceed original price"
            )

    return errors


def is_valid_product(product):

    return len(validate_product(product)) == 0