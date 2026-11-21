from pathlib import Path

from processors.pipeline import process_and_store_category_pages
from storage.export_manager import export_all_formats
from storage.database import DEFAULT_DB_PATH
from config.logging_config import setup_logging


# Category configuration.
CATEGORY_CONFIG = {

    "Original Packaging": {
        "source_url": (
            "https://tomkardy.com.ua/ua/"
            "g44619880-originalnaya-upakovka-oae"
        ),

        "html_files": [
            "data/raw/original_packaging_multiple.html"
        ]
    },

    "Perfume Testers": {
        "source_url": (
            "https://tomkardy.com.ua/ua/"
            "g35061078-tester-oae"
        ),

        "html_files": [
            "data/raw/perfume_testers_multiple.html",
            "data/raw/perfume_testers_page_2.html"
        ]
    }

}


def load_html_pages(file_paths):
    """
    Loads saved HTML files from the local data directory.
    """

    html_pages = []

    for file_path in file_paths:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"HTML file not found: {path}"
            )

        with open(path, "r", encoding="utf-8") as file:
            html_pages.append(file.read())

        print(f"Loaded HTML file: {path}")

    return html_pages


def main():

    # Initialize application logging.
    logger = setup_logging()

    logger.info("Application started.")

    print("\n===================================")
    print(" E-COMMERCE PRODUCT INTELLIGENCE")
    print("===================================\n")

    category_summaries = {}

    # Process each product category.
    for category, configuration in CATEGORY_CONFIG.items():

        print(f"\nProcessing category: {category}")
        print("-----------------------------------")

        logger.info(f"Processing category: {category}")

        # Load saved HTML pages.
        html_pages = load_html_pages(
            configuration["html_files"]
        )

        logger.info(
            f"Loaded {len(html_pages)} HTML pages for {category}"
        )

        # Process and store valid products.
        results = process_and_store_category_pages(
            page_html_list=html_pages,
            category=category,
            source_url=configuration["source_url"],
            db_path=DEFAULT_DB_PATH
        )

        category_summaries[category] = results

        logger.info(
            f"{category}: "
            f"{results['total_valid']} valid products, "
            f"{results['total_invalid']} invalid products, "
            f"{results['duplicates_removed']} duplicates removed."
        )

        print("\nCategory Summary")
        print(f"Pages processed: {results['pages_processed']}")
        print(f"Valid products: {results['total_valid']}")
        print(f"Invalid products: {results['total_invalid']}")
        print(f"Duplicates removed: {results['duplicates_removed']}")
        print(
            f"Database records processed: "
            f"{results['saved_to_database']}"
        )

    # Export all database records.
    print("\n===================================")
    print(" EXPORTING PRODUCT DATA")
    print("===================================")

    export_results = export_all_formats(
        db_path=DEFAULT_DB_PATH,
        output_directory="data/processed"
    )

    # Log export results.
    logger.info("Data export completed.")

    logger.info(
        f"Exported {export_results['excel_records']} records to Excel."
    )

    logger.info(
        f"Exported {export_results['csv_records']} records to CSV."
    )

    logger.info(
        f"Exported {export_results['json_records']} records to JSON."
    )

    # Final application summary.
    print("\n===================================")
    print(" APPLICATION COMPLETED")
    print("===================================")

    print("\nCategory Results:")

    for category, results in category_summaries.items():

        print(
            f"{category}: "
            f"{results['total_valid']} valid products"
        )

    print("\nExport Results:")

    print(f"Excel: {export_results['excel_path']}")
    print(f"CSV:   {export_results['csv_path']}")
    print(f"JSON:  {export_results['json_path']}")

    print("\nProduct processing completed successfully.")

    logger.info("Application completed successfully.")


if __name__ == "__main__":
    main()
