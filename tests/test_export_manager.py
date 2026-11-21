import json

from openpyxl import load_workbook

from storage.database import initialize_database, save_products
from storage.export_manager import export_all_formats


def test_export_all_formats(tmp_path):

    db_path = tmp_path / "test_products.db"
    output_directory = tmp_path / "exports"

    initialize_database(db_path)

    product = {
        "product_id": "2001",
        "product_code": "TEST001",
        "product_name": "Test Perfume",
        "product_url": "https://example.com/product",
        "original_price": 2000.0,
        "current_price": 1800.0,
        "currency": "UAH",
        "discount": "-10%",
        "availability": "Available"
    }

    save_products(
        [product],
        "Perfume Testers",
        "https://example.com/category",
        db_path
    )

    results = export_all_formats(
        db_path=db_path,
        output_directory=str(output_directory)
    )

    # Verify export counts.
    assert results["excel_records"] == 1
    assert results["csv_records"] == 1
    assert results["json_records"] == 1

    # Verify files exist.
    assert (output_directory / "products.xlsx").exists()
    assert (output_directory / "products.csv").exists()
    assert (output_directory / "products.json").exists()

    # Verify Excel content.
    workbook = load_workbook(output_directory / "products.xlsx")

    assert "Perfume Testers" in workbook.sheetnames

    # Verify JSON content.
    with open(
        output_directory / "products.json",
        encoding="utf-8"
    ) as file:

        products = json.load(file)

    assert len(products) == 1
    assert products[0]["product_id"] == "2001"