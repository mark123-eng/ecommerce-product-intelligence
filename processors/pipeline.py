from collections import defaultdict

from processors.product_parser import (
    extract_product,
    extract_products
)

from processors.cleaning import clean_product
from processors.validation import validate_product

from scrapers.dummyjson_api import DummyJSONAPIClient

from storage.database import (
    initialize_database,
    save_products,
    DEFAULT_DB_PATH,
    DEFAULT_SOURCE
)

from config.logging_config import setup_logging


# Initialize application logger.
logger = setup_logging()


def process_product_html(html):
    """
    Extracts, cleans and validates one HTML product.
    """

    logger.info(
        "Starting single product processing."
    )

    product = extract_product(html)

    if product is None:

        logger.warning(
            "No product card found in supplied HTML."
        )

        return {
            "product": None,
            "is_valid": False,
            "errors": ["No product card found"]
        }

    cleaned_product = clean_product(product)

    logger.info(
        f"Cleaned product: "
        f"{cleaned_product.get('product_name')}"
    )

    errors = validate_product(cleaned_product)

    if errors:

        logger.warning(
            f"Product validation failed: {errors}"
        )

    else:

        logger.info(
            f"Product validated successfully: "
            f"{cleaned_product.get('product_name')}"
        )

    return {
        "product": cleaned_product,
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def process_category_pages(page_html_list):
    """
    Processes products across multiple category HTML pages.

    Extracts, cleans, validates and removes duplicate products.
    """

    logger.info(
        f"Starting category processing for "
        f"{len(page_html_list)} HTML pages."
    )

    valid_products = []
    invalid_products = []

    seen_product_ids = set()
    duplicates_removed = 0

    for page_number, page_html in enumerate(
        page_html_list,
        start=1
    ):

        products = extract_products(page_html)

        logger.info(
            f"Page {page_number}: "
            f"{len(products)} products extracted."
        )

        print(
            f"Page {page_number}: "
            f"{len(products)} products extracted"
        )

        for product in products:

            cleaned_product = clean_product(product)

            product_id = cleaned_product.get(
                "product_id"
            )

            if (
                product_id
                and product_id in seen_product_ids
            ):

                duplicates_removed += 1

                logger.warning(
                    f"Duplicate product detected: {product_id}"
                )

                continue

            if product_id:
                seen_product_ids.add(product_id)

            errors = validate_product(cleaned_product)

            if errors:

                invalid_products.append({
                    "product": cleaned_product,
                    "errors": errors
                })

                logger.warning(
                    f"Invalid product {product_id}: {errors}"
                )

            else:

                valid_products.append(cleaned_product)

    results = {
        "pages_processed": len(page_html_list),
        "valid_products": valid_products,
        "invalid_products": invalid_products,
        "duplicates_removed": duplicates_removed,
        "total_valid": len(valid_products),
        "total_invalid": len(invalid_products)
    }

    logger.info(
        f"Category processing completed. "
        f"Valid: {results['total_valid']}, "
        f"Invalid: {results['total_invalid']}, "
        f"Duplicates: {results['duplicates_removed']}."
    )

    return results


def process_and_store_category_pages(
    page_html_list,
    category,
    source_url,
    db_path=DEFAULT_DB_PATH,
    source=DEFAULT_SOURCE
):
    """
    Processes HTML category pages and saves valid products into SQLite.
    """

    logger.info(
        f"Starting processing and database storage "
        f"for: {category}"
    )

    initialize_database(db_path)

    results = process_category_pages(page_html_list)

    saved_count = save_products(
        products=results["valid_products"],
        category=category,
        source_url=source_url,
        db_path=db_path,
        source=source
    )

    results["saved_to_database"] = saved_count

    logger.info(
        f"Database storage completed for {category}. "
        f"Records processed: {saved_count}."
    )

    return results


def process_api_products(
    api_products,
    api_client=None
):
    """
    Processes raw API product records.

    Normalizes, cleans, validates and removes duplicate products.

    API records are converted into the application's standardized
    product schema before entering the existing processing pipeline.
    """

    logger.info(
        f"Starting API product processing. "
        f"Records received: {len(api_products)}"
    )

    if api_client is None:

        api_client = DummyJSONAPIClient()

    valid_products = []
    invalid_products = []

    seen_product_ids = set()

    duplicates_removed = 0

    for raw_product in api_products:

        try:

            # Convert API JSON into the standard product schema.
            normalized_product = api_client.normalize_product(
                raw_product
            )

            # Preserve the original API category.
            category = normalized_product.get(
                "category"
            )

            # Apply existing cleaning logic.
            cleaned_product = clean_product(
                normalized_product
            )

            # Ensure category survives cleaning.
            cleaned_product["category"] = category

            product_id = cleaned_product.get(
                "product_id"
            )

            # Detect duplicate API records.
            if (
                product_id
                and product_id in seen_product_ids
            ):

                duplicates_removed += 1

                logger.warning(
                    f"Duplicate API product detected: {product_id}"
                )

                continue

            if product_id:

                seen_product_ids.add(product_id)

            # Apply existing validation logic.
            errors = validate_product(
                cleaned_product
            )

            if errors:

                invalid_products.append({
                    "product": cleaned_product,
                    "errors": errors
                })

                logger.warning(
                    f"Invalid API product {product_id}: {errors}"
                )

            else:

                valid_products.append(
                    cleaned_product
                )

        except (ValueError, TypeError) as error:

            invalid_products.append({
                "product": raw_product,
                "errors": [str(error)]
            })

            logger.warning(
                f"API product processing failed: {error}"
            )

    results = {

        "valid_products": valid_products,

        "invalid_products": invalid_products,

        "duplicates_removed": duplicates_removed,

        "total_received": len(api_products),

        "total_valid": len(valid_products),

        "total_invalid": len(invalid_products)

    }

    logger.info(
        f"API processing completed. "
        f"Received: {results['total_received']}, "
        f"Valid: {results['total_valid']}, "
        f"Invalid: {results['total_invalid']}, "
        f"Duplicates: {results['duplicates_removed']}."
    )

    return results


def process_and_store_api_products(
    api_products,
    source_url=DummyJSONAPIClient.BASE_URL,
    db_path=DEFAULT_DB_PATH,
    source=DummyJSONAPIClient.SOURCE,
    api_client=None
):
    """
    Processes API products and stores valid records in SQLite.

    Products are grouped by their original API categories before
    database insertion.
    """

    logger.info(
        f"Starting API processing and database storage "
        f"for source: {source}"
    )

    initialize_database(db_path)

    results = process_api_products(
        api_products=api_products,
        api_client=api_client
    )

    # Group valid products by their API category.
    products_by_category = defaultdict(list)

    for product in results["valid_products"]:

        category = (
            product.get("category")
            or "uncategorized"
        )

        products_by_category[category].append(
            product
        )

    saved_count = 0

    # Save each category separately.
    for category, products in products_by_category.items():

        category_saved = save_products(
            products=products,
            category=category,
            source_url=source_url,
            db_path=db_path,
            source=source
        )

        saved_count += category_saved

        logger.info(
            f"Stored {category_saved} products "
            f"under category: {category}"
        )

    results["saved_to_database"] = saved_count

    logger.info(
        f"API database storage completed. "
        f"Total records saved: {saved_count}."
    )

    return results