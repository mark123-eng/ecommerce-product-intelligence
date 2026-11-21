from storage.database import initialize_database, save_products
from storage.excel_exporter import export_to_excel

import pandas as pd


def test_excel_export(tmp_path):

    db_path = tmp_path / "test_products.db"
    excel_path = tmp_path / "products.xlsx"

    initialize_database(db_path)

    products = [
        {
            "product_id": "1001",
            "product_code": "P001",
            "product_name": "Perfume A",
            "product_url": "https://example.com/a",
            "original_price": 1500.0,
            "current_price": 1200.0,
            "currency": "UAH",
            "discount": "-20%",
            "availability": "Available"
        },
        {
            "product_id": "1002",
            "product_code": "P002",
            "product_name": "Perfume B",
            "product_url": "https://example.com/b",
            "original_price": 2000.0,
            "current_price": 1800.0,
            "currency": "UAH",
            "discount": "-10%",
            "availability": "Available"
        }
    ]

    save_products(
        products,
        category="Perfume Testers",
        source_url="https://example.com/category",
        db_path=db_path
    )

    exported_count = export_to_excel(
        output_path=excel_path,
        db_path=db_path
    )

    assert exported_count == 2
    assert excel_path.exists()

    exported_df = pd.read_excel(
        excel_path,
        sheet_name="Perfume Testers"
    )

    assert len(exported_df) == 2
    assert "product_name" in exported_df.columns