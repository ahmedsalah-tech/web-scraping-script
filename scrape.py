import os, hashlib, requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE = "https://laravel.com"
START = "https://laravel.com/docs/11.x"

OUT = "site"
PAGES = f"{OUT}/pages"
ASSETS = f"{OUT}/assets"

os.makedirs(PAGES, exist_ok=True)
os.makedirs(ASSETS, exist_ok=True)

seen_assets = {}
seen_pages = set()

def asset_name(url):
    ext = os.path.splitext(urlparse(url).path)[1]
    return hashlib.md5(url.encode()).hexdigest() + ext

def save_asset(url):
    if url in seen_assets:
        return seen_assets[url]

    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
    except:
        return None

    name = asset_name(url)
    path = f"{ASSETS}/{name}"

    with open(path, "wb") as f:
        f.write(r.content)

    local = f"../assets/{name}"
    seen_assets[url] = local
    return local

def page_name(url):
    return (url.rstrip("/").split("/")[-1] or "index") + ".html"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(START)
    page.wait_for_load_state("networkidle")

    links = page.eval_on_selector_all(
        "nav a[href^='/docs']",
        "els => [...new Set(els.map(e => e.href))]"
    )

    for url in links:
        if url in seen_pages:
            continue
        seen_pages.add(url)

        print("Scraping:", url)
        page.goto(url)
        page.wait_for_load_state("networkidle")

        soup = BeautifulSoup(page.content(), "html.parser")

        # --- ASSETS ---
        for tag, attr in [("img","src"), ("link","href"), ("script","src")]:
            for el in soup.find_all(tag):
                src = el.get(attr)
                if not src or src.startswith("data:"):
                    continue
                full = urljoin(BASE, src)
                local = save_asset(full)
                if local:
                    el[attr] = local

        # --- PATCH INTERNAL NAVIGATION ---
        for a in soup.find_all("a", href=True):
            href = a["href"]

            if href.startswith("/docs/"):
                local = page_name(href)
                a["href"] = local

            elif href.startswith(BASE + "/docs/"):
                local = page_name(href)
                a["href"] = local

        # Save page
        filename = page_name(url)
        with open(f"{PAGES}/{filename}", "w", encoding="utf-8") as f:
            f.write(str(soup))

    browser.close()
