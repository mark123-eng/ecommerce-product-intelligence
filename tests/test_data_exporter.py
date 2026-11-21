import json

from storage.database import initialize_database, save_products
from storage.data_exporter import export_to_csv, export_to_json


def test_csv_and_json_exports(tmp_path):

    db_path = tmp_path / "test_products.db"
    csv_path = tmp_path / "products.csv"
    json_path = tmp_path / "products.json"

    # Initialize temporary database.
    initialize_database(db_path)

    # Sample product.
    product = {
        "product_id": "1001",
        "product_code": "OP001",
        "product_name": "Original Packaging Perfume",
        "product_url": "https://example.com/product1",
        "original_price": 2000.0,
        "current_price": 1800.0,
        "currency": "UAH",
        "discount": "-10%",
        "availability": "Available"
    }

    # Save product into the database.
    save_products(
        [product],
        "Original Packaging",
        "https://example.com/original",
        db_path
    )

    # Test CSV export.
    csv_count = export_to_csv(
        db_path=db_path,
        output_path=csv_path
    )

    assert csv_count == 1
    assert csv_path.exists()

    # Test JSON export.
    json_count = export_to_json(
        db_path=db_path,
        output_path=json_path
    )

    assert json_count == 1
    assert json_path.exists()

    # Verify JSON content.
    with open(json_path, encoding="utf-8") as file:
        exported_products = json.load(file)

    assert len(exported_products) == 1
    assert exported_products[0]["product_id"] == "1001"

    assert (
        exported_products[0]["product_name"]
        == "Original Packaging Perfume"
    )