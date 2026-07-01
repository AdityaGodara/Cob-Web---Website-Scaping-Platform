import time


def scrape(url: str):
    print(f"Scraping {url}")

    time.sleep(10)

    return {
        "title": f"Dummy title for {url}",
        "content": "Dummy content"
    }