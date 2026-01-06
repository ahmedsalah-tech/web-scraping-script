# Web Scraping

This small project scrapes the Laravel documentation site by default.

If you'd like to scrape a different site, feel free to fork this repository and change the base URL used by the scraper. Also update any Laravel-specific paths to their corresponding paths on the new site.

Quick notes:
- Currently configured to scrape the Laravel docs.
- To target a different site, edit `scrape.py` and update the base URL (look for a variable named like `BASE_URL` or `base_url`) to the new domain.
- Update any Laravel-specific routes or URLs in the code to match the structure of the site you want to scrape.

Usage
-----
Run the scraper with Python:

```powershell
python scrape.py
```

Contributing
------------
Any changes are welcome — fork the repo, change the base URL and any related paths, and open a PR if you'd like to contribute improvements.

License
-------
This repository doesn't include a license file. Add one if you plan to distribute or allow contributions under a specific license.

