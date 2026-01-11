import os
import hashlib
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


# Prompt for URL
try:
    start_url = input("Enter the starting documentation URL: ")
    if not start_url.startswith("http"):
        print("Error: Please enter a valid URL starting with http or https.")
        exit(1)
except (KeyboardInterrupt, EOFError):
    print("\nExiting.")
    exit(0)

# Parse URL for base and path
parsed_url = urlparse(start_url)
BASE_URL = f"{parsed_url.scheme}://{parsed_url.netloc}"
DOCS_BASE_PATH = parsed_url.path.rstrip("/")
START_URL = start_url


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
    parsed = urlparse(url)
    path = parsed.path

    # Normalize path
    path = path.rstrip("/")

    # Root / docs base path -> index.html
    if not path or path == "/" or path == DOCS_BASE_PATH:
        return "index.html"

    else:
        rel_path = path.lstrip("/")

    # Fallback to index if nothing remains
    if not rel_path:
        rel_path = "index"

    # Replace directory separators to preserve structure in a flat directory
    base_name = rel_path.replace("/", "_")

    # If this URL is on a different host, prefix with the host to avoid collisions
    base_netloc = urlparse(BASE_URL).netloc
    if parsed.netloc and parsed.netloc != base_netloc:
        safe_netloc = parsed.netloc.replace(":", "_").replace(".", "_")
        base_name = f"{safe_netloc}_{base_name}"

    return base_name + ".html"
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


def patch_navigation(soup: BeautifulSoup, base_url: str, docs_base_path: str):
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        if not href:
            continue

        # Resolve the link to an absolute URL
        absolute_url = urljoin(base_url, href)

        # Check if it's a documentation link
        if absolute_url.startswith(base_url + docs_base_path):
            # Rewrite the link to point to the local file
            a["href"] = page_filename(absolute_url)



with sync_playwright() as p:
    browser = p.chromium.launch(       
        executable_path="C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        headless=True
    )
    page = browser.new_page(user_agent=USER_AGENT)

    print("Loading index...")
    page.goto(START_URL, timeout=120000)
    page.wait_for_load_state("load")

    # Dynamic selector for documentation links
    nav_selector = f"nav a[href^='{DOCS_BASE_PATH}'], nav a[href^='{BASE_URL}{DOCS_BASE_PATH}']"
    body_selector = f"body a[href^='{DOCS_BASE_PATH}'], body a[href^='{BASE_URL}{DOCS_BASE_PATH}']"

    # Discover links in both nav and body
    nav_links = page.eval_on_selector_all(nav_selector, "els => [...new Set(els.map(e => e.href))]")
    body_links = page.eval_on_selector_all(body_selector, "els => [...new Set(els.map(e => e.href))]")
    
    links = sorted(list(set(nav_links + body_links)))

    if not links:
        print("No documentation links found. Exiting.")
        exit(1)

    for url in links:
        filename = page_filename(url)
        out_path = os.path.join(PAGES_DIR, filename)

        if os.path.exists(out_path):
            print(f"Skipping (already downloaded): {url}")
            continue

        print(f"Scraping: {url}")

        try:
            page.goto(url, wait_until="load", timeout=120000)
            time.sleep(REQUEST_DELAY_SEC)

        except Exception as e:
            print(f"Failed to load {url}: {e}")

            with open("failed_pages.log", "a", encoding="utf-8") as log:
                log.write(url + "\n")

            continue

        soup = BeautifulSoup(page.content(), "html.parser")

        patch_assets(soup, url)
        patch_navigation(soup, BASE_URL, DOCS_BASE_PATH)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

    browser.close()

print("\nDone.")
print("Open site/pages/index.html to view offline.")
