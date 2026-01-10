# Offline Documentation Scraper

This script downloads a documentation website for offline browsing. It uses Playwright to render JavaScript-heavy pages and BeautifulSoup to parse the HTML, rewrite links, and save assets locally.

## How It Works

1. **URL Input**: The script prompts you to enter the starting URL of the documentation you want to download.
2. **Link Discovery**: It loads the starting page and discovers all unique documentation links within the site's navigation and body.
3. **Scraping**: It visits each discovered link, saving the page content.
4. **Asset Handling**: It downloads all referenced assets (CSS, JS, images) and saves them to a local `site/assets` directory.
5. **Link Patching**: It rewrites all links in the saved HTML files to point to the local downloaded pages and assets, allowing for complete offline navigation.

The final static site is saved in the `site/` directory.

## Requirements

* Python 3.10+
* `requests`
* `beautifulsoup4`
* `playwright`

## Setup

1. **Install Python packages**:

    ```powershell
    pip install requests beautifulsoup4 playwright
    ```

2. **Install Playwright browsers**:
    The script uses Playwright to control a headless browser. You must install the necessary browser binaries by running the following command:

    ```powershell
    python -m playwright install
    ```

    This will download the default browsers (like Chromium) that Playwright uses to render pages.

## Configuration

### Browser

By default, the script is configured to use a specific local installation of Brave Browser. If you want to use Playwright's built-in browser, you must edit `scrape.py`.

Locate the following lines in `scrape.py`:

```python
    browser = p.chromium.launch(
        executable_path="C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        headless=True
    )
```

To use the default browser, remove the `executable_path` line:

```python
    browser = p.chromium.launch(
        headless=True
    )
```

Ensure you have run `python -m playwright install` so that the default browser is available.

## Usage

1. Run the script from your terminal:

    ```powershell
    python scrape.py
    ```

2. When prompted, enter the full starting URL for the documentation you wish to download (e.g., `https://laravel.com/docs/11.x/installation`).

3. The script will begin scraping the site. The output will be saved in the `site/` directory.

4. Once finished, open `site/pages/index.html` in your browser to view the offline documentation.
