import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import time
import random
import os

BASE_URL = "https://www.olympedia.org/athletes/{}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

SAVE_BIOS = "data/raw/bios_raw.csv"
SAVE_RESULTS = "data/raw/results_raw.csv"
SAVE_ERRORS = "data/raw/errors_list.txt"


# -------------------------------------------
# SAFE REQUEST with RETRIES (Slow Mode)
# -------------------------------------------
def safe_request(url):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code == 200:
                return r
        except Exception:
            time.sleep(2 ** attempt)  # exponential backoff: 1s → 2s → 4s
    return None


# -------------------------------------------
# PARSE BIO DATA
# -------------------------------------------
def get_bio(soup, athlete_id):
    table = soup.find("table", {"class": "biodata"})
    if table is None:
        return None

    df = pd.read_html(StringIO(str(table)), index_col=0)[0].T
    df["athlete_id"] = athlete_id
    return df


# -------------------------------------------
# PARSE RESULTS DATA
# -------------------------------------------
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


# -------------------------------------------
# SCRAPE RANGE & APPEND
# -------------------------------------------
def scrape_range(start, end):
    # Load existing data
    if os.path.exists(SAVE_BIOS):
        bios_existing = pd.read_csv(SAVE_BIOS)
    else:
        bios_existing = pd.DataFrame()

    if os.path.exists(SAVE_RESULTS):
        results_existing = pd.read_csv(SAVE_RESULTS)
    else:
        results_existing = pd.DataFrame()

    new_bios = []
    new_results = []
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
            new_bios.append(bio)

        res = get_results(soup, i)
        if res is not None:
            new_results.append(res)

        # Slow Mode (0.6 to 1.5 seconds)
        time.sleep(random.uniform(0.6, 1.5))

    # Append Mode (NO DUPLICATES)
    if new_bios:
        bio_df = pd.concat(new_bios, ignore_index=True)
        combined_bios = pd.concat([bios_existing, bio_df], ignore_index=True)
        combined_bios.drop_duplicates(subset=["athlete_id"], keep="first", inplace=True)
        combined_bios.to_csv(SAVE_BIOS, index=False)
        print("Updated bios_raw.csv")

    if new_results:
        res_df = pd.concat(new_results, ignore_index=True)
        combined_results = pd.concat([results_existing, res_df], ignore_index=True)
        combined_results.to_csv(SAVE_RESULTS, index=False)
        print("Updated results_raw.csv")

    # Save errors
    with open(SAVE_ERRORS, "a") as f:
        f.write("\n" + str(errors))

    print("Phase 2 complete!")


# -------------------------------------------
# RUN SCRAPER
# -------------------------------------------
if __name__ == "__main__":
    scrape_range(101, 1000)
