from urllib.parse import urljoin


def generate_page_urls(category_url, total_pages):
    """
    Generates URLs for all pages in a category.

    Page 1 uses the original category URL.
    Pages 2 onwards use the /page_N pattern.
    """

    page_urls = [category_url]

    for page_number in range(2, total_pages + 1):

        page_url = urljoin(
            category_url.rstrip("/") + "/",
            f"page_{page_number}"
        )

        page_urls.append(page_url)

    return page_urls