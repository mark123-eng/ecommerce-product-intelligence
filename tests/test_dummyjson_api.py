import pytest

from scrapers.dummyjson_api import DummyJSONAPIClient


class FakeResponse:

    def __init__(self, data, status_code=200):

        self.data = data
        self.status_code = status_code

    def raise_for_status(self):

        if self.status_code >= 400:

            import requests

            raise requests.HTTPError(
                f"HTTP {self.status_code}"
            )

    def json(self):

        return self.data


class FakeSession:

    def __init__(self, responses):

        self.responses = responses
        self.calls = []
        self.closed = False

    def get(self, url, params, timeout):

        self.calls.append({
            "url": url,
            "params": params,
            "timeout": timeout
        })

        return self.responses.pop(0)

    def close(self):

        self.closed = True


def sample_product(product_id=1):

    return {

        "id": product_id,

        "title": "Essence Mascara Lash Princess",

        "description": "Sample product",

        "category": "beauty",

        "price": 9.99,

        "discountPercentage": 10.0,

        "rating": 4.5,

        "stock": 50,

        "sku": "BEA-ESS-001",

        "availabilityStatus": "In Stock"

    }


def test_fetch_page():

    response = FakeResponse({

        "products": [sample_product()],

        "total": 1,

        "skip": 0,

        "limit": 30

    })

    session = FakeSession([response])

    client = DummyJSONAPIClient(
        session=session
    )

    result = client.fetch_page()

    assert len(result["products"]) == 1

    assert result["total"] == 1

    assert session.calls[0]["params"] == {
        "limit": 30,
        "skip": 0
    }


def test_fetch_all_products_with_pagination():

    first_page = FakeResponse({

        "products": [
            sample_product(1),
            sample_product(2)
        ],

        "total": 3,

        "skip": 0,

        "limit": 2

    })

    second_page = FakeResponse({

        "products": [
            sample_product(3)
        ],

        "total": 3,

        "skip": 2,

        "limit": 2

    })

    session = FakeSession([
        first_page,
        second_page
    ])

    client = DummyJSONAPIClient(
        session=session
    )

    products = client.fetch_all_products(
        limit=2
    )

    assert len(products) == 3

    assert len(session.calls) == 2

    assert session.calls[0]["params"]["skip"] == 0

    assert session.calls[1]["params"]["skip"] == 2


def test_normalize_product():

    client = DummyJSONAPIClient()

    product = sample_product()

    normalized = client.normalize_product(
        product
    )

    assert normalized["product_id"] == "1"

    assert normalized["product_name"] == (
        "Essence Mascara Lash Princess"
    )

    assert normalized["current_price"] == 9.99

    assert normalized["original_price"] is None

    assert normalized["currency"] == "USD"

    assert normalized["discount"] == "10.00%"

    assert normalized["product_code"] == "BEA-ESS-001"


def test_normalize_product_missing_id():

    client = DummyJSONAPIClient()

    product = sample_product()

    product.pop("id")

    with pytest.raises(ValueError):

        client.normalize_product(product)


def test_invalid_api_response():

    response = FakeResponse({

        "total": 1,

        "skip": 0,

        "limit": 30

    })

    session = FakeSession([response])

    client = DummyJSONAPIClient(
        session=session
    )

    with pytest.raises(ValueError):

        client.fetch_page()


def test_invalid_price():

    client = DummyJSONAPIClient()

    product = sample_product()

    product["price"] = "invalid"

    with pytest.raises(ValueError):

        client.normalize_product(product)


def test_invalid_pagination_limit():

    client = DummyJSONAPIClient()

    with pytest.raises(ValueError):

        client.fetch_all_products(limit=0)


def test_session_closes():

    session = FakeSession([])

    with DummyJSONAPIClient(
        session=session
    ):

        pass

    assert session.closed is True