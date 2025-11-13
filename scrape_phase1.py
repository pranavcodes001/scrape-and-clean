import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import os
import time
import random

BASE_URL = "https://www.olympedia.org/athletes/{}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

SAVE_BIOS = "data/raw/bios_raw.csv"
SAVE_RESULTS = "data/raw/results_raw.csv"
SAVE_ERRORS = "data/raw/errors_list.txt"


def safe_request(url):
    """Retry 3 times before giving up."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                return r
        except Exception:
            time.sleep(2 ** attempt)  # exponential backoff
    return None


def get_bio(soup, athlete_id):
    table = soup.find("table", {"class": "biodata"})
    if table is None:
        return None

    df = pd.read_html(StringIO(str(table)), index_col=0)[0].T
    df["athlete_id"] = athlete_id
    return df


def get_results(soup, athlete_id):
    table = soup.find("table", {"class": "table"})
    if table is None:
        return None

    df = pd.read_html(StringIO(str(table)))[0]
    df["athlete_id"] = athlete_id
    df["NOC"] = None
    df["Discipline"] = None

    if "Games" not in df.columns:
        return None

    rows_to_keep = df.index[df["Games"].isna()].tolist()
    rows_with_games = df.index[~df["Games"].isna()].tolist()

    if rows_with_games:
        if "NOC / Team" in df.columns:
            df.loc[rows_with_games, "NOC"] = df.loc[rows_with_games, "NOC / Team"]
        if "Discipline (Sport) / Event" in df.columns:
            df.loc[rows_with_games, "Discipline"] = df.loc[rows_with_games, "Discipline (Sport) / Event"]

    for col in ["Games", "NOC", "As", "Discipline"]:
        if col in df.columns:
            df[col] = df[col].ffill()

    df = df.rename(columns={
        "Discipline (Sport) / Event": "Event",
        "NOC / Team": "Team"
    })

    df = df.drop(columns=["Unnamed: 6"], errors="ignore")

    return df.iloc[rows_to_keep] if rows_to_keep else None


def scrape_range(start, end):
    bios = []
    results = []
    errors = []

    for i in range(start, end + 1):
        print(f"Scraping athlete {i}...")

        url = BASE_URL.format(i)
        r = safe_request(url)

        if r is None:
            errors.append(i)
            continue

        soup = BeautifulSoup(r.content, "html.parser")

        bio = get_bio(soup, i)
        if bio is not None:
            bios.append(bio)

        res = get_results(soup, i)
        if res is not None:
            results.append(res)

        time.sleep(random.uniform(0.4, 1.2))

    # Save outputs
    if bios:
        bio_df = pd.concat(bios, ignore_index=True)
        bio_df.to_csv(SAVE_BIOS, mode="w", index=False)
        print("Saved bios_raw.csv")

    if results:
        res_df = pd.concat(results, ignore_index=True)
        res_df.to_csv(SAVE_RESULTS, mode="w", index=False)
        print("Saved results_raw.csv")

    with open(SAVE_ERRORS, "w") as f:
        f.write(str(errors))

    print("Phase 1 complete!")


if __name__ == "__main__":
    scrape_range(1, 100)
