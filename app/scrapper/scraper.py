import httpx
from bs4 import BeautifulSoup


class ScraperError(Exception):
    pass



def scrape(url: str) -> dict:
    try:
        with httpx.Client(
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/137.0 Safari/537.36"
                )
            },
        ) as client:

            response = client.get(url)
            response.raise_for_status()
    except httpx.TimeoutException:
        raise ScraperError("Request timed out")

    except httpx.ConnectError:
        raise ScraperError("Unable to connect")

    except httpx.HTTPStatusError as e:
        raise ScraperError(f"HTTP {e.response.status_code}")

    except Exception as e:
        raise ScraperError(str(e))

    soup = BeautifulSoup(response.text, "lxml")

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    meta_description = None

    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        meta_description = meta.get("content")

    h1_tags = [
        h1.get_text(strip=True)
        for h1 in soup.find_all("h1")
    ]

    links = []

    for link in soup.find_all("a", href=True):
        links.append(link["href"])

    return {
        "title": title,
        "meta_description": meta_description,
        "h1": h1_tags,
        "links": links,
        "status_code": response.status_code,
    }
