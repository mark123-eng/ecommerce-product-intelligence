from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from scrapers.perfume_scraper import (
    USER_AGENT,
    CATEGORY_URLS
)


TIMEOUT = 30


def inspect_robots():

    print("=" * 65)
    print(" E-COMMERCE PRODUCT INTELLIGENCE")
    print(" ROBOTS.TXT PERMISSION DIAGNOSTIC")
    print("=" * 65)

    print("\nUser-Agent:", USER_AGENT)

    origins = {}

    for category, category_url in CATEGORY_URLS.items():

        parsed = urlparse(category_url)

        origin = (
            f"{parsed.scheme}://{parsed.netloc}"
        )

        robots_url = f"{origin}/robots.txt"

        if origin not in origins:

            origins[origin] = {
                "robots_url": robots_url,
                "parser": None,
                "verified": False
            }

    session = requests.Session()

    session.headers.update({
        "User-Agent": USER_AGENT
    })

    try:

        for origin, information in origins.items():

            robots_url = information["robots_url"]

            print("\n" + "-" * 65)
            print("Checking:", robots_url)

            try:

                response = session.get(
                    robots_url,
                    timeout=TIMEOUT
                )

                print(
                    "HTTP status:",
                    response.status_code
                )

                print(
                    "Content type:",
                    response.headers.get(
                        "Content-Type",
                        "Not specified"
                    )
                )

                print(
                    "Retry-After:",
                    response.headers.get(
                        "Retry-After",
                        "Not specified"
                    )
                )

                if response.status_code == 429:

                    print(
                        "RESULT: RATE LIMITED."
                    )

                    print(
                        "Permission cannot be verified."
                    )

                    continue

                response.raise_for_status()

                content_type = response.headers.get(
                    "Content-Type",
                    ""
                ).lower()

                body = response.text.strip().lower()

                html_indicators = (
                    "<!doctype html",
                    "<html",
                    "<head",
                    "<body",
                    "<form",
                    "recaptcha",
                    "bot protection"
                )

                if "text/html" in content_type or any(
                    marker in body
                    for marker in html_indicators
                ):

                    print(
                        "RESULT: INVALID ROBOTS RESPONSE."
                    )

                    print(
                        "HTML or bot-protection content detected."
                    )

                    continue

                parser = RobotFileParser()

                parser.set_url(robots_url)

                parser.parse(
                    response.text.splitlines()
                )

                information["parser"] = parser

                information["verified"] = True

                print(
                    "RESULT: ROBOTS.TXT RETRIEVED AND VALIDATED."
                )

            except requests.RequestException as error:

                print(
                    "RESULT: REQUEST FAILED."
                )

                print("Reason:", error)

            except Exception as error:

                print(
                    "RESULT: VALIDATION FAILED."
                )

                print("Reason:", error)

        print("\n" + "=" * 65)
        print("CATEGORY PERMISSION RESULTS")
        print("=" * 65)

        for category, category_url in CATEGORY_URLS.items():

            parsed = urlparse(category_url)

            origin = (
                f"{parsed.scheme}://{parsed.netloc}"
            )

            information = origins[origin]

            print("\nCategory:", category)

            print("URL:", category_url)

            if not information["verified"]:

                print(
                    "Permission: UNKNOWN"
                )

                print(
                    "Action: DO NOT SCRAPE."
                )

                continue

            allowed = information["parser"].can_fetch(
                USER_AGENT,
                category_url
            )

            if allowed:

                print(
                    "Permission: ALLOWED BY ROBOTS.TXT"
                )

            else:

                print(
                    "Permission: DISALLOWED BY ROBOTS.TXT"
                )

        print("\n" + "=" * 65)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 65)

    finally:

        session.close()


if __name__ == "__main__":

    inspect_robots()