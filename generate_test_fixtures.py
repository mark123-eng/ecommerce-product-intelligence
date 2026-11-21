from pathlib import Path


# Directory where synthetic HTML fixtures will be stored.
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def create_product_card(
    product_id,
    product_code,
    product_name,
    original_price,
    current_price
):
    """
    Generates one synthetic e-commerce product card.

    The HTML structure mirrors the CSS selectors expected
    by processors/product_parser.py.
    """

    return f"""
    <li class="cs-product-gallery__item"
        data-product-id="{product_id}">

        <a class="cs-goods-title"
           href="https://shop.example.test/products/{product_id}">
            {product_name}
        </a>

        <button
            data-product-id="{product_id}"
            data-product-price="{original_price} UAH"
            data-product-discounted-price="{current_price} UAH">
        </button>

        <div class="cs-product-gallery__sku">
            <span>{product_code}</span>
        </div>

        <span data-qaid="discount_label">
            Synthetic discount
        </span>

        <span data-qaid="presence_data">
            In stock
        </span>

    </li>
    """


def create_page(products):
    """
    Wraps product cards inside a complete HTML document.
    """

    cards = "\n".join(products)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Synthetic Product Catalogue</title>
    </head>
    <body>
        <ul class="product-list">
            {cards}
        </ul>
    </body>
    </html>
    """


def save_html(filename, html):
    """
    Saves generated HTML to the raw data directory.
    """

    file_path = RAW_DIR / filename

    file_path.write_text(
        html,
        encoding="utf-8"
    )

    print(f"Generated: {file_path}")


def generate_sample_products():
    """
    Generates individual product-card fixtures.

    Used by product parser and pipeline unit tests.
    """

    product = create_product_card(
        product_id="SYN-0001",
        product_code="SYN-CODE-001",
        product_name="Synthetic Eau de Parfum Example",
        original_price=2030,
        current_price=1750
    )

    tester = create_product_card(
        product_id="SYN-TESTER-0001",
        product_code="SYN-CODE-002",
        product_name="Synthetic Tester Fragrance Example",
        original_price=1230,
        current_price=1050
    )

    save_html(
        "sample_product_card.html",
        create_page([product])
    )

    save_html(
        "sample_tester_product_card.html",
        create_page([tester])
    )


def generate_category_pages():
    """
    Generates synthetic category pages.

    Original Packaging:
        24 products on one page.

    Perfume Testers:
        48 products distributed across two pages.
        24 products per page.
    """

    original_products = []

    for number in range(1, 25):

        product = create_product_card(
            product_id=f"SYN-ORIGINAL-{number:03d}",
            product_code=f"ORIGINAL-{number:03d}",
            product_name=f"Synthetic Original Product {number}",
            original_price=2000 + number * 10,
            current_price=1800 + number * 10
        )

        original_products.append(product)

    save_html(
        "original_packaging_multiple.html",
        create_page(original_products)
    )

    tester_page_one = []
    tester_page_two = []

    for number in range(1, 49):

        product = create_product_card(
            product_id=f"SYN-TESTER-{number:03d}",
            product_code=f"TESTER-{number:03d}",
            product_name=f"Synthetic Tester Product {number}",
            original_price=1200 + number * 10,
            current_price=1000 + number * 10
        )

        if number <= 24:
            tester_page_one.append(product)

        else:
            tester_page_two.append(product)

    save_html(
        "perfume_testers_multiple.html",
        create_page(tester_page_one)
    )

    save_html(
        "perfume_testers_page_2.html",
        create_page(tester_page_two)
    )


def main():
    """
    Generates all synthetic HTML fixtures.
    """

    print("\nGenerating synthetic product fixtures...\n")

    generate_sample_products()

    generate_category_pages()

    print("\nAll synthetic fixtures generated successfully.\n")

    print("Generated HTML files:")

    for file_path in sorted(RAW_DIR.glob("*.html")):

        print(
            f"{file_path.name}: "
            f"{file_path.stat().st_size:,} bytes"
        )


if __name__ == "__main__":
    main()