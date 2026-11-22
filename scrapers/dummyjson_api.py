import requests

from config.logging_config import setup_logging


logger = setup_logging()


class DummyJSONAPIClient:
    """
    Client for retrieving product data from DummyJSON.

    Handles API requests, pagination, response validation
    and product normalization.
    """

    BASE_URL = "https://dummyjson.com/products"
    SOURCE = "dummyjson.com"

    DEFAULT_LIMIT = 30
    DEFAULT_TIMEOUT = 20

    # Explicit application assumption.
    # DummyJSON does not supply a currency field.
    DEFAULT_CURRENCY = "USD"

    def __init__(
        self,
        timeout=DEFAULT_TIMEOUT,
        currency=DEFAULT_CURRENCY,
        session=None
    ):

        self.timeout = timeout
        self.currency = currency

        self.session = session or requests.Session()

    def fetch_page(self, limit=DEFAULT_LIMIT, skip=0):
        """
        Retrieve one page of products from the API.
        """

        if limit <= 0:
            raise ValueError("Limit must be greater than zero.")

        if skip < 0:
            raise ValueError("Skip cannot be negative.")

        params = {
            "limit": limit,
            "skip": skip
        }

        logger.info(
            f"Requesting DummyJSON products: "
            f"limit={limit}, skip={skip}"
        )

        try:

            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException:

            logger.exception(
                "DummyJSON API request failed."
            )

            raise

        except ValueError:

            logger.exception(
                "DummyJSON returned invalid JSON."
            )

            raise

        if not isinstance(data, dict):

            raise ValueError(
                "API response must be a JSON object."
            )

        products = data.get("products")

        total = data.get("total")

        if not isinstance(products, list):

            raise ValueError(
                "API response does not contain a valid products list."
            )

        if not isinstance(total, int) or total < 0:

            raise ValueError(
                "API response contains an invalid total."
            )

        if not all(isinstance(product, dict) for product in products):

            raise ValueError(
                "API products must contain JSON objects."
            )

        logger.info(
            f"Retrieved {len(products)} products."
        )

        return data

    def fetch_all_products(self, limit=DEFAULT_LIMIT):
        """
        Retrieve all available products using pagination.
        """

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than zero."
            )

        all_products = []

        skip = 0

        total = None

        while total is None or skip < total:

            data = self.fetch_page(
                limit=limit,
                skip=skip
            )

            products = data["products"]

            total = data["total"]

            if not products:
                break

            all_products.extend(products)

            skip += len(products)

            logger.info(
                f"Pagination progress: "
                f"{len(all_products)}/{total}"
            )

        logger.info(
            f"Completed API extraction. "
            f"Total products retrieved: {len(all_products)}"
        )

        return all_products

    def normalize_product(self, product):
        """
        Convert a DummyJSON product into the application's
        standardized product structure.
        """

        product_id = product.get("id")

        if product_id is None:

            raise ValueError(
                "API product is missing its ID."
            )

        title = product.get("title")

        if not isinstance(title, str) or not title.strip():

            raise ValueError(
                f"API product {product_id} has an invalid title."
            )

        price = product.get("price")

        if isinstance(price, bool) or not isinstance(
            price,
            (int, float)
        ):

            raise ValueError(
                f"API product {product_id} has an invalid price."
            )

        discount_percentage = product.get(
            "discountPercentage"
        )

        discount = None

        if discount_percentage is not None:

            if isinstance(discount_percentage, bool) or not isinstance(
                discount_percentage,
                (int, float)
            ):

                raise ValueError(
                    f"API product {product_id} has an invalid discount."
                )

            discount = f"{discount_percentage:.2f}%"

        normalized = {

            "product_id": str(product_id),

            "product_code": product.get("sku"),

            "product_name": title,
            "category": product.get("category"),

            "product_url": (
                f"https://dummyjson.com/products/{product_id}"
            ),

            # DummyJSON does not provide original_price.
            "original_price": None,

            "current_price": float(price),

            # Explicit application assumption.
            "currency": self.currency,

            "discount": discount,

            "availability": product.get(
                "availabilityStatus"
            )

        }

        return normalized

    def close(self):
        """
        Close the HTTP session.
        """

        self.session.close()

        logger.info(
            "DummyJSON API session closed."
        )

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.close()