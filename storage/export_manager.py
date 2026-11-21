from storage.excel_exporter import export_to_excel
from storage.data_exporter import export_to_csv, export_to_json

from storage.database import DEFAULT_DB_PATH


def export_all_formats(
    db_path=DEFAULT_DB_PATH,
    output_directory="data/processed"
):
    """
    Exports all database products into Excel, CSV and JSON.
    """

    excel_path = f"{output_directory}/products.xlsx"
    csv_path = f"{output_directory}/products.csv"
    json_path = f"{output_directory}/products.json"

    print("\nStarting data export...\n")

    # Export to Excel.
    excel_count = export_to_excel(
        db_path=db_path,
        output_path=excel_path
    )

    # Export to CSV.
    csv_count = export_to_csv(
        db_path=db_path,
        output_path=csv_path
    )

    # Export to JSON.
    json_count = export_to_json(
        db_path=db_path,
        output_path=json_path
    )

    print("\nExport Summary")
    print("--------------------------")
    print(f"Excel records: {excel_count}")
    print(f"CSV records:   {csv_count}")
    print(f"JSON records:  {json_count}")

    return {
        "excel_records": excel_count,
        "csv_records": csv_count,
        "json_records": json_count,
        "excel_path": excel_path,
        "csv_path": csv_path,
        "json_path": json_path
    }