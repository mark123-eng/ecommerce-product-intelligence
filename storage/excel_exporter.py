import pandas as pd
import re

from pathlib import Path

from storage.database import get_all_products, DEFAULT_DB_PATH


def export_to_excel(
    db_path=DEFAULT_DB_PATH,
    output_path="data/processed/products.xlsx"
):
    """
    Exports database products into an Excel workbook.

    Each product category gets its own worksheet.
    """

    products = get_all_products(db_path)

    if not products:
        print("No products available for export.")
        return 0

    dataframe = pd.DataFrame(products)

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with pd.ExcelWriter(
        output_path,
        engine="openpyxl"
    ) as writer:

        for category, category_data in dataframe.groupby("category"):

            # Replace characters that Excel prohibits in sheet names.
            sheet_name = re.sub(
                r'[\\/*?:\[\]]',
                "_",
                str(category)
            )[:31]

            category_data.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

    print(f"Excel export successful: {output_path}")

    return len(dataframe)