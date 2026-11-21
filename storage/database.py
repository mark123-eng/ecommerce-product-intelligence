import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config.logging_config import setup_logging


logger = setup_logging()

DEFAULT_DB_PATH = Path("data/processed/products.db")


def get_connection(db_path=DEFAULT_DB_PATH):
    """
    Establish a connection to the SQLite database.
    """

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        logger.info(f"Database connection established: {db_path}")

        return connection

    except sqlite3.Error:
        logger.exception("Database connection failed.")
        raise


def initialize_database(db_path=DEFAULT_DB_PATH):
    """
    Create the normalized database structure.

    Automatically migrates the previous database schema
    while preserving existing product records.
    """

    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'products'
        """)

        products_table_exists = cursor.fetchone() is not None

        if products_table_exists:

            cursor.execute("PRAGMA table_info(products)")
            columns = {
                row["name"]
                for row in cursor.fetchall()
            }

            # Migrate the previous database structure.
            if "category" in columns:

                logger.info("Old database schema detected. Starting migration.")

                cursor.execute("""
                    ALTER TABLE products
                    RENAME TO products_legacy
                """)

        # Main products table.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (

                product_id TEXT NOT NULL,
                source TEXT NOT NULL,

                product_code TEXT,
                product_name TEXT NOT NULL,
                product_url TEXT NOT NULL,

                original_price REAL,
                current_price REAL NOT NULL,

                currency TEXT NOT NULL,
                discount TEXT,
                availability TEXT,

                PRIMARY KEY (product_id, source)

            )
        """)

        # Product-category relationship table.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_categories (

                product_id TEXT NOT NULL,
                source TEXT NOT NULL,

                category TEXT NOT NULL,
                source_url TEXT,
                collected_at TEXT NOT NULL,

                PRIMARY KEY (
                    product_id,
                    source,
                    category
                ),

                FOREIGN KEY (product_id, source)
                REFERENCES products(product_id, source)
                ON DELETE CASCADE

            )
        """)

        # Preserve records from the previous schema.
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'products_legacy'
        """)

        legacy_exists = cursor.fetchone() is not None

        if legacy_exists:

            logger.info("Migrating existing product records.")

            cursor.execute("""
                INSERT OR IGNORE INTO products (
                    product_id,
                    source,
                    product_code,
                    product_name,
                    product_url,
                    original_price,
                    current_price,
                    currency,
                    discount,
                    availability
                )
                SELECT
                    product_id,
                    source,
                    product_code,
                    product_name,
                    product_url,
                    original_price,
                    current_price,
                    currency,
                    discount,
                    availability
                FROM products_legacy
            """)

            cursor.execute("""
                INSERT OR IGNORE INTO product_categories (
                    product_id,
                    source,
                    category,
                    source_url,
                    collected_at
                )
                SELECT
                    product_id,
                    source,
                    category,
                    source_url,
                    collected_at
                FROM products_legacy
                WHERE category IS NOT NULL
            """)

            cursor.execute("DROP TABLE products_legacy")

            logger.info("Database migration completed successfully.")

        connection.commit()

        logger.info("Database initialized successfully.")

    except Exception:

        connection.rollback()

        logger.exception("Database initialization failed.")

        raise

    finally:

        connection.close()


def save_products(
    products,
    category,
    source_url,
    db_path=DEFAULT_DB_PATH
):
    """
    Save products and their category relationships.
    """

    connection = get_connection(db_path)

    saved_count = 0

    source = "tomkardy.com.ua"

    collected_at = datetime.now(timezone.utc).isoformat()

    try:

        cursor = connection.cursor()

        for product in products:

            cursor.execute("""
                INSERT INTO products (
                    product_id,
                    source,
                    product_code,
                    product_name,
                    product_url,
                    original_price,
                    current_price,
                    currency,
                    discount,
                    availability
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(product_id, source)

                DO UPDATE SET

                    product_code = excluded.product_code,
                    product_name = excluded.product_name,
                    product_url = excluded.product_url,
                    original_price = excluded.original_price,
                    current_price = excluded.current_price,
                    currency = excluded.currency,
                    discount = excluded.discount,
                    availability = excluded.availability

            """, (

                product["product_id"],
                source,
                product.get("product_code"),
                product["product_name"],
                product["product_url"],
                product.get("original_price"),
                product["current_price"],
                product["currency"],
                product.get("discount"),
                product.get("availability")

            ))

            cursor.execute("""
                INSERT INTO product_categories (

                    product_id,
                    source,
                    category,
                    source_url,
                    collected_at

                )

                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(
                    product_id,
                    source,
                    category
                )

                DO UPDATE SET

                    source_url = excluded.source_url,
                    collected_at = excluded.collected_at

            """, (

                product["product_id"],
                source,
                category,
                source_url,
                collected_at

            ))

            saved_count += 1

        connection.commit()

        logger.info(
            f"Successfully saved {saved_count} product-category records "
            f"for {category}."
        )

        return saved_count

    except Exception:

        connection.rollback()

        logger.exception(
            f"Failed to save products for category: {category}"
        )

        raise

    finally:

        connection.close()


def get_all_products(db_path=DEFAULT_DB_PATH):
    """
    Retrieve products together with their category information.

    A product belonging to multiple categories will appear
    once for each product-category relationship.
    """

    connection = get_connection(db_path)

    try:

        cursor = connection.cursor()

        cursor.execute("""

            SELECT

                p.product_id,
                p.source,
                p.product_code,
                p.product_name,
                p.product_url,
                p.original_price,
                p.current_price,
                p.currency,
                p.discount,
                p.availability,

                pc.category,
                pc.source_url,
                pc.collected_at

            FROM products p

            LEFT JOIN product_categories pc

                ON p.product_id = pc.product_id
                AND p.source = pc.source

            ORDER BY p.product_name, pc.category

        """)

        products = [
            dict(row)
            for row in cursor.fetchall()
        ]

        logger.info(
            f"Retrieved {len(products)} product-category records."
        )

        return products

    except sqlite3.Error:

        logger.exception("Failed to retrieve products.")

        raise

    finally:

        connection.close()