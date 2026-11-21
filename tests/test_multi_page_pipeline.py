from pathlib import Path

from processors.pipeline import (
    process_category_pages,
    process_and_store_category_pages,
)

from processors.product_parser import extract_products

from storage.database import get_all_products


RAW_DIR = Path("data/raw")


def read_fixture(filename):

    return (RAW_DIR / filename).read_text(encoding="utf-8")


def test_multi_page_processing():

    page_one = read_fixture(
        "original_packaging_multiple.html"
    )

    page_two = read_fixture(
        "original_packaging_multiple.html"
    )

    results = process_category_pages([
        page_one,
        page_two,
    ])

    assert results["pages_processed"] == 2
    assert results["total_valid"] == 24
    assert results["total_invalid"] == 0
    assert results["duplicates_removed"] == 24


def test_process_two_different_tester_pages():

    page_one = read_fixture(
        "perfume_testers_multiple.html"
    )

    page_two = read_fixture(
        "perfume_testers_page_2.html"
    )

    products_page_one = extract_products(page_one)
    products_page_two = extract_products(page_two)

    results = process_category_pages([
        page_one,
        page_two,
    ])

    assert len(products_page_one) == 24
    assert len(products_page_two) == 24

    assert results["pages_processed"] == 2
    assert results["duplicates_removed"] == 0
    assert results["total_valid"] == 48
    assert results["total_invalid"] == 0


def test_process_and_store_two_tester_pages(tmp_path):

    page_one = read_fixture(
        "perfume_testers_multiple.html"
    )

    page_two = read_fixture(
        "perfume_testers_page_2.html"
    )

    test_db = tmp_path / "integrated_products.db"

    results = process_and_store_category_pages(
        page_html_list=[
            page_one,
            page_two,
        ],
        category="Synthetic Perfume Testers",
        source_url="https://shop.example.test/testers",
        db_path=test_db,
    )

    database_products = get_all_products(test_db)

    assert results["pages_processed"] == 2
    assert results["total_valid"] == 48
    assert results["saved_to_database"] == 48

    assert len(database_products) == 48

    assert all(
        product["category"] == "Synthetic Perfume Testers"
        for product in database_products
    )