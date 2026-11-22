from scrapers.dummyjson_api import DummyJSONAPIClient

from processors.pipeline import process_and_store_api_products

from storage.export_manager import export_all_formats


def main():

    print("=" * 60)
    print("E-COMMERCE PRODUCT INTELLIGENCE SYSTEM")
    print("API DATA EXTRACTION PIPELINE")
    print("=" * 60)

    try:

        # 1. Connect to the API.
        with DummyJSONAPIClient() as client:

            print("\nConnecting to DummyJSON API...")

            # 2. Retrieve all available products.
            raw_products = client.fetch_all_products()

            print(f"Successfully retrieved {len(raw_products)} products.")

            # 3. Process and store products.
            print("\nProcessing product records...")

            results = process_and_store_api_products(
                api_products=raw_products,
                api_client=client
            )

        # 4. Display processing summary.
        print("\nPROCESSING SUMMARY")
        print("-" * 40)

        print(f"Products received: {results['total_received']}")
        print(f"Valid products: {results['total_valid']}")
        print(f"Invalid products: {results['total_invalid']}")
        print(f"Duplicates removed: {results['duplicates_removed']}")
        print(f"Database records saved: {results['saved_to_database']}")

        # 5. Export database records.
        export_results = export_all_formats()

        # 6. Final summary.
        print("\nEXPORT SUMMARY")
        print("-" * 40)

        print(f"Excel records: {export_results['excel_records']}")
        print(f"CSV records: {export_results['csv_records']}")
        print(f"JSON records: {export_results['json_records']}")

        print("\nOUTPUT FILES")
        print("-" * 40)

        print(export_results["excel_path"])
        print(export_results["csv_path"])
        print(export_results["json_path"])

        print("\nPIPELINE COMPLETED SUCCESSFULLY.")

    except Exception as error:

        print("\nPIPELINE FAILED.")
        print(f"Error: {error}")

        raise


if __name__ == "__main__":
    main()