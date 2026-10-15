import argparse
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

from .config import load_config
from .merge import merge_entries
from .notion import iter_pages, process_block, query_block


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export Notion pages as one merged CSV entry per UTC day.")
    parser.add_argument("--output", type=Path, default=Path("data.csv"), help="Output CSV path (default: data.csv)")
    args = parser.parse_args(argv)
    try:
        token, database_id = load_config()
    except ValueError as error:
        parser.error(str(error))

    with requests.Session() as session:
        session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json",
        })
        pages = list(iter_pages(session, database_id))
        print(f"Retrieved {len(pages)} Notion pages. Extracting text...")
        entries = [
            {
                "id": page["id"],
                "ts": page["created_time"],
                "text": process_block(session, query_block(session, page["id"])),
            }
            for page in tqdm(pages, desc="Extracting text", unit="page", disable=None)
        ]

    daily = merge_entries(pd.DataFrame(entries, columns=["id", "ts", "text"]))
    daily.to_csv(args.output, index=False)
    print(f"Saved {len(daily)} daily entries to {args.output}")


if __name__ == "__main__":
    main()
