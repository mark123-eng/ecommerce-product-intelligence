from scrapers.pagination import generate_page_urls


def test_original_packaging_pagination():

    category_url = (
        "https://tomkardy.com.ua/ua/"
        "g44619880-originalnaya-upakovka-oae"
    )

    urls = generate_page_urls(category_url, 17)

    assert len(urls) == 17

    assert urls[0] == category_url

    assert urls[1].endswith("/page_2")

    assert urls[-1].endswith("/page_17")

    print("\nGenerated URLs:", len(urls))
    print("First URL:", urls[0])
    print("Second URL:", urls[1])
    print("Last URL:", urls[-1])




















def test_perfume_testers_pagination():

    category_url = (
        "https://tomkardy.com.ua/ua/"
        "g35061078-tester-oae"
    )

    urls = generate_page_urls(category_url, 23)

    assert len(urls) == 23

    assert urls[0] == category_url

    assert urls[1].endswith("/page_2")

    assert urls[-1].endswith("/page_23")

    print("\nTester URLs:", len(urls))
    print("First URL:", urls[0])
    print("Last URL:", urls[-1])