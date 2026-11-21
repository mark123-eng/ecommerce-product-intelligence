
from scrapers.perfume_scraper import (
    PerfumeScraper,
    CATEGORY_URLS
)

from processors.pipeline import (
    process_and_store_category_pages
)

from storage.export_manager import export_all_formats

from storage.database import DEFAULT_DB_PATH

from config.logging_config import setup_logging


logger = setup_logging()


# Map website category identifiers to application categories.
CATEGORY_NAMES = {
    "original_packaging": "Original Packaging",
    "testers": "Perfume Testers"
}


def main():

    logger.info("Live scraping application started.")

    print("\n===================================")
    print(" E-COMMERCE PRODUCT INTELLIGENCE")
    print(" LIVE SCRAPING MODE")
    print("===================================\n")

    category_summaries = {}

    scraper = PerfumeScraper()

    try:

        # Process each configured website category.
        for category_key, source_url in CATEGORY_URLS.items():

            category = CATEGORY_NAMES[category_key]

            print(f"\nProcessing category: {category}")
            print("-----------------------------------")

            logger.info(
                "Starting live scraping for %s",
                category
            )

            # Retrieve raw HTML pages.
            html_pages = scraper.scrape_category_pages(
                category=category,
                start_url=source_url
            )

            if not html_pages:

                logger.warning(
                    "No HTML pages collected for %s",
                    category
                )

                print(
                    f"No pages collected for {category}."
                )

                continue

            logger.info(
                "Collected %s HTML pages for %s",
                len(html_pages),
                category
            )

            # Process HTML through the existing pipeline.
            results = process_and_store_category_pages(
                page_html_list=html_pages,
                category=category,
                source_url=source_url,
                db_path=DEFAULT_DB_PATH
            )

            category_summaries[category] = results

            print("\nCategory Summary")

            print(
                f"Pages processed: "
                f"{results['pages_processed']}"
            )

            print(
                f"Valid products: "
                f"{results['total_valid']}"
            )

            print(
                f"Invalid products: "
                f"{results['total_invalid']}"
            )

            print(
                f"Duplicates removed: "
                f"{results['duplicates_removed']}"
            )

            print(
                f"Database records processed: "
                f"{results['saved_to_database']}"
            )

            logger.info(
                "%s completed: %s valid, %s invalid.",
                category,
                results["total_valid"],
                results["total_invalid"]
            )

    finally:

        # Always close the HTTP session.
        scraper.close()

    # Export database records.
    print("\n===================================")
    print(" EXPORTING PRODUCT DATA")
    print("===================================")

    export_results = export_all_formats(
        db_path=DEFAULT_DB_PATH,
        output_directory="data/processed"
    )

    print("\nExport Results")

    print(
        f"Excel: {export_results['excel_path']}"
    )

    print(
        f"CSV: {export_results['csv_path']}"
    )

    print(
        f"JSON: {export_results['json_path']}"
    )

    print("\n===================================")
    print(" LIVE SCRAPING COMPLETED")
    print("===================================")

    logger.info(
        "Live scraping application completed."
    )


if __name__ == "__main__":
    main()
