import os
import hashlib
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


BASE_URL = "https://laravel.com"
START_URL = "https://laravel.com/docs/12.x"

OUTPUT_DIR = "site"
PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets")

REQUEST_DELAY_SEC = 1.0  # for rate limiting

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

downloaded_assets: dict[str, str] = {}
downloaded_pages: set[str] = set()

def page_already_downloaded(url: str) -> bool:
    return os.path.exists(os.path.join(PAGES_DIR, page_filename(url)))


def hash_filename(url: str) -> str:
    ext = os.path.splitext(urlparse(url).path)[1]
    return hashlib.md5(url.encode()).hexdigest() + ext


def save_asset(url: str) -> str | None:
    if url in downloaded_assets:
        return downloaded_assets[url]

    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
    except Exception:
        return None

    filename = hash_filename(url)
    filepath = os.path.join(ASSETS_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(r.content)

    local_path = f"../assets/{filename}"
    downloaded_assets[url] = local_path
    return local_path


def page_filename(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    return (slug or "index") + ".html"


def patch_assets(soup: BeautifulSoup, page_url: str):
    for tag, attr in [("img", "src"), ("link", "href"), ("script", "src")]:
        for el in soup.find_all(tag):
            src = el.get(attr)
            if not src or src.startswith("data:"):
                continue

            full_url = urljoin(page_url, src)
            local = save_asset(full_url)
            if local:
                el[attr] = local


def patch_navigation(soup: BeautifulSoup):
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("/docs/"):
            a["href"] = page_filename(href)

        elif href.startswith(BASE_URL + "/docs/"):
            a["href"] = page_filename(href)



with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        headless=True
    )
    page = browser.new_page(user_agent=USER_AGENT)

    print("Loading index...")
    page.goto(START_URL)
    page.wait_for_load_state("networkidle")

    links = page.eval_on_selector_all(
        "nav a[href^='/docs']",
        "els => [...new Set(els.map(e => e.href))]"
    )

    for url in links:
        filename = page_filename(url)
        out_path = os.path.join(PAGES_DIR, filename)

        if os.path.exists(out_path):
            print(f"Skipping (already downloaded): {url}")
            continue

        print(f"Scraping: {url}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_load_state("networkidle", timeout=60000)
            time.sleep(REQUEST_DELAY_SEC)

        except Exception as e:
            print(f"Failed to load {url}: {e}")

            with open("failed_pages.log", "a", encoding="utf-8") as log:
                log.write(url + "\n")

            continue

        soup = BeautifulSoup(page.content(), "html.parser")

        patch_assets(soup, url)
        patch_navigation(soup)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

    browser.close()

print("\nDone.")
print("Open site/pages/index.html to view offline.")
