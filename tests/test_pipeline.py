from pathlib import Path

from processors.pipeline import process_product_html


def test_pipeline_processes_product():

    html = Path(
        "data/raw/sample_product_card.html"
    ).read_text(encoding="utf-8")

    result = process_product_html(html)

    assert result["is_valid"] is True
    assert result["errors"] == []

    product = result["product"]

    assert product["product_id"] == "SYN-0001"
    assert product["product_code"] == "SYN-CODE-001"
    assert product["original_price"] == 2030.0
    assert product["current_price"] == 1750.0


def test_pipeline_handles_missing_product():

    result = process_product_html(
        "<html><body></body></html>"
    )

    assert result["is_valid"] is False
    assert result["product"] is None
    assert "No product card found" in result["errors"]