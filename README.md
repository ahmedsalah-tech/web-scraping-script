# Web Scraping

This small project scrapes the Laravel documentation site by default.

If you'd like to scrape a different site, feel free to fork this repository and change the base URL used by the scraper. Also update any Laravel-specific paths to their corresponding paths on the new site.

Quick notes:

Usage
Run the scraper with Python:

```powershell
python scrape.py
```

Contributing
Any changes are welcome — fork the repo, change the base URL and any related paths, and open a PR if you'd like to contribute improvements.

License
This repository doesn't include a license file. Add one if you plan to distribute or allow contributions under a specific license.

## Install

Install dependencies with pip:

```powershell
python -m pip install --upgrade pip
python -m pip install beautifulsoup4 playwright requests uvicorn

# If you use Playwright, install browser binaries as well:
python -m playwright install
```

Or install from the project metadata:

```powershell
python -m pip install .
```

## Usage

Run the scraper with Python:

```powershell
python scrape.py
```

## Browser executable

This project does not use Playwright's headless browser by default. Instead, it expects you to provide (or change) a browser executable path to one you prefer. Edit `scrape.py` and look for where the browser is launched (search for `launch(`, `executable_path`, or `executablePath`).

Set the executable path to your preferred browser binary and ensure headless mode is disabled. Example (Playwright, Python):

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
	# Change the path below to the browser executable you want to use
	browser = p.chromium.launch(headless=False, executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
	page = browser.new_page()
	page.goto("https://laravel.com/docs")
	# ... your scraping logic

	browser.close()
```

Notes:

- Depending on which Playwright API you use (sync/async) or which language binding, the parameter name may be `executable_path` or `executablePath` — search for either.
- Ensure `headless=False` (or omit headless) so the browser runs in headed mode.
- If you prefer to use the browser that Playwright installed, you can omit `executable_path` and let Playwright launch its managed browser; this project defaults to a non-headless, custom-executable setup.


