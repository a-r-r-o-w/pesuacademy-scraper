
PESUAcademy-Scraper
=====================

Notes/Slides scraper for [PESU Academy](https://www.pesuacademy.com)

### Requirements
```py
pip install -r requirements.txt
cd src
```

### Usage
```py
python3 download.py -s semester username password
```

As an example, let's scrape notes and slides for Semester 3:

```py
python3 download.py -s 3 PES1UG20XY123 MySuperSecretPassword
```

Additionally, you can specify whether or not you want console logging to be enabled while scraping (enabled by default).
- To disable logging, use `-q` or `--quiet`
- To enable debug logging, use `-v` or `--verbose`
