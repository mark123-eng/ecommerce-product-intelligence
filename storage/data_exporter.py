import json
from pathlib import Path

import pandas as pd

from storage.database import get_all_products, DEFAULT_DB_PATH


def export_to_csv(
    db_path=DEFAULT_DB_PATH,
    output_path="data/processed/products.csv"
):
    """
    Exports all database products into a CSV file.
    """

    products = get_all_products(db_path)

    if not products:
        print("No products available for CSV export.")
        return 0

    dataframe = pd.DataFrame(products)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"CSV export successful: {output_path}")

    return len(products)


def export_to_json(
    db_path=DEFAULT_DB_PATH,
    output_path="data/processed/products.json"
):
    """
    Exports all database products into a JSON file.
    """

    products = get_all_products(db_path)

    if not products:
        print("No products available for JSON export.")
        return 0

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(
            products,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"JSON export successful: {output_path}")

    return len(products)
