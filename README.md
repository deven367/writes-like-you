# Writes like you!

This is just a fun project I am working on to essentially **train a language model to write like me** with all the text that I have written in Notion over the course of 2 years.

## Steps

* [x] Explore the Notion API
* [x] Iteratively query the DB to fetch all the text written in a given Notion Database
* [x] Generate csv file containing all the text
* [x] Fine - tune a language model
* [x] Check the results
* [x] Move onto the next project :)

## Setup

### Prerequisites

This project assumes that you have setup your `Notion Developer Account` and have the secret `NOTION_TOKEN` and the `NOTION_DATABASE_ID` that you wish to query.

Requires Python 3.13 or newer and uv. `.python-version` pins local commands to Python 3.13.

Set up the project with uv and make:

```sh
make sync
test -f .env || cp .env.example .env
chmod 600 .env
```

Dependencies are declared in `pyproject.toml`; `uv.lock` records the exact versions. `make sync` installs the locked environment. After changing dependencies, run `uv lock` to update the lockfile.

Set `NOTION_TOKEN` and `NOTION_DATABASE_ID` in the project-root `.env`. This file is ignored by Git. `wlu/config.py` loads it at CLI startup, independently of the working directory. Environment variables take precedence over `.env` values.

The Makefile has only three targets: `make sync`, `make test`, and `make run`. `make test` runs the offline behavioral and configuration checks without Notion credentials or API requests.

Application source lives in `wlu/`; notebooks live in the root-level `nbs/` folder. Run `make run` to write `data.csv` without an interactive prompt. Choose another full output path with `make run OUTPUT=daily.csv`, or invoke the CLI directly with `uv run --locked python -m wlu --output daily.csv`.

The CSV contains exactly one row per **UTC creation date**, sorted by date:

* `id`: comma-separated IDs of all Notion pages merged into the row.
* `ts`: the earliest creation timestamp for that date.
* `date`: the UTC date derived from `created_time`, not a custom Notion date property.
* `text`: all entries in timestamp order, separated by blank lines. Rich-text segments, paginated blocks, headings, lists, and nested blocks are included.

Requests run sequentially to respect Notion's rate limit. API failures stop the export instead of silently saving missing text. Existing CSV snapshots are not rewritten; rerun the exporter to generate a daily-merged file.

For fine-tuning, run `make run` to create the ignored `data.csv` in the project root, then open `nbs/finetune.ipynb` with `nbs/` as the notebook working directory. The notebook installs its separate training dependencies.

To run Python commands directly, activate the environment with `source .venv/bin/activate`.
