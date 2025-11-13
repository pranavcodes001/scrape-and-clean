Olympic Athletes – Web Scraping & Data Cleaning

This project collects athlete information from Olympedia.org and cleans it into a structured dataset that can be used for analysis.
The goal was to practice Python web scraping, handle messy data, and organize a real-world cleaning workflow using Pandas.

Project Structure

project-root/
│
├── scrape_phase1.py        # Scrapes first batch of athletes
├── scrape_phase2.py        # Continues scraping next range
├── clean.ipynb             # Data cleaning + merging + exploration
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── bios_raw.csv
│   │   ├── results_raw.csv
│   │   └── errors_list.txt
│   │
│   └── clean/
│       ├── bios_clean.csv
│       ├── results_clean.csv
│       └── combined_athletes.csv
│
└── README.md

What This Project Does
1. Scraping

Each athlete lives at a unique URL:
https://www.olympedia.org/athletes/<id>

Two scripts (scrape_phase1.py and scrape_phase2.py) fetch:

Bio details (name, roles, height/weight, birth/death info, NOC…)

Competition results (Games, events, medals…)

The scraper runs in slow-mode with retries so the website isn’t hammered.

All scraped data is saved into:

data/raw/bios_raw.csv
data/raw/results_raw.csv

2. Cleaning

All cleaning and merging happens inside clean.ipynb.

Main steps:

Remove duplicate athlete entries

Fix inconsistent columns

Forward-fill event info where needed

Clean strings (e.g., remove stray symbols, fix mixed formats)

Standardize Games names, medal types, and NOC fields

Join bios and results into one final file

Output files:

data/clean/bios_clean.csv
data/clean/results_clean.csv
data/clean/combined_athletes.csv

Why Olympedia?

The site has:

messy, inconsistent HTML

tables with mixed data

missing and broken rows

lots of edge cases

This makes it a good dataset to practice real-world cleaning techniques instead of working with already-clean CSVs.

Tech Used

Python
BeautifulSoup
Requests
Pandas
NumPy
Jupyter Notebook

How to Run

Create a virtual env:

python -m venv scrape
.venv\Scripts\activate

Install requirements:

pip install -r requirements.txt

Run scraping (example):

python scrape_phase1.py
python scrape_phase2.py

Open the notebook and run cleaning:

jupyter notebook clean.ipynb

Notes
Raw data is intentionally kept in the repo so the scraping work is visible.
The scraper is written in a way that can continue from where it left off.
The project can be extended to scrape more IDs or focus on specific sports.