# Agent notes

## Layout and commands

- Application source is the `wlu/` package. Run commands from the repository root.
- Use Python 3.13, pinned by `.python-version`; `pyproject.toml` requires Python >=3.13.
- The Makefile has exactly three targets: `make sync` installs the locked uv environment, `make test` runs offline regressions, and `make run` exports the database.
- `make run` invokes `uv run --locked python -m wlu --output "$(OUTPUT)"`. `OUTPUT` defaults to `data.csv`; override it with a full output path, including the extension. There is no interactive filename prompt.
- `wlu/__main__.py` is the only command entry point. The redundant `n2.py`, `n3.py`, and legacy root-level exporter were removed; do not add compatibility wrappers.
- Notebooks belong in root-level `nbs/`, not `wlu/`. Start `nbs/finetune.ipynb` with `nbs/` as its working directory; its data-loading cell reads `../data.csv`.
- Training dependencies are installed by the notebook, separately from the exporter dependencies in `pyproject.toml` and `uv.lock`.
- Keep `.env` at the repository root; copy `.env.example` if needed. `wlu/config.py:load_config` resolves it relative to its own path at CLI startup, not at import time or relative to the working directory. Existing environment variables take precedence. Never print or commit credentials or journal text.

## Daily-entry contract

- Exactly one logical CSV record per UTC creation date, sorted by date. The date comes from Notion `created_time`, not the database's custom `Created` date property. Do not silently change that convention.
- Columns remain `id`, `ts`, `date`, and `text`.
- Sort source entries by timestamp, with page ID as the tie-breaker, before grouping.
- Preserve every source page ID as a comma-separated `id` value; use the earliest timestamp as `ts`.
- Join nonempty entry texts with blank lines. Preserve all text, including identical text from distinct source entries. Do not keep only the first row or deduplicate by text.
- CSV text can contain quoted newlines. Count records with a CSV parser, not physical file lines.
- Existing CSV/Excel snapshots are not automatically migrated or rewritten. Regenerate exports to get the corrected behavior.

## Failure causes and implementation constraints

- The original exporters did not aggregate by date at all: sorting by date still left one row per Notion page. `wlu/merge.py:merge_entries` now performs aggregation independently of configuration or API access.
- The original active exporter kept only the first rich-text segment of each paragraph. Extraction must retain every segment, preserve block boundaries, and traverse nested blocks and all block-pagination pages. Headings and lists can contain text too.
- The old `n3.py` assigned `imap_unordered` results positionally to DataFrame rows, potentially attaching text to the wrong page/date. Preserve the page-to-text association if parallelism is ever restored.
- The old threaded-prefetch/process-pool combination also relied on a process-local cache; spawned macOS workers do not share that cache. Do not restore that design.
- Current requests are sequential, with a 0.35-second pause per request, to stay below Notion's average three-requests-per-second limit. Any future parallel implementation needs a shared limiter first.
- HTTP failures must raise, not become empty text or an apparently exhausted database. Fetch/extract/merge before writing the CSV so API failures do not produce a partial export.

## Verification evidence and limits

- `make sync` and `make test` passed after the refactor. Five offline tests cover startup configuration precedence and working-directory independence, missing credentials, empty output headers, complete export behavior, and preservation of an existing CSV when a later block request fails.
- The pipeline regression covers database pagination, block pagination, multiple rich-text segments, nested headings/list items, out-of-order entries, UTC normalization, and empty text.
- A smoke run on `latest.csv` merged 973 source entries into 792 daily records; every source ID and all text were preserved through CSV serialization and parsing. The snapshot itself was not modified.
- The relocated notebook's data-loading cell passed against both a temporary parent-level `data.csv` and the real live export. Merged text and UTC timestamp parsing passed. Model training was not exercised.
- A full refactored `make run` completed under Python 3.13.9: 1,237 Notion pages became 1,036 daily records. CSV-parser checks confirmed unique, sorted UTC dates, all 1,237 unique source IDs retained, and every field (including merged text) identical to the verified pre-refactor root `data.csv`. The notebook's CSV-loading cell also passed under 3.13. Repeat completed-CSV checks after future changes; a successful API probe alone does not establish end-to-end success.
- CLI smoke checks passed with credentials removed and dotenv disabled: `python -m wlu --help` works; running an export without settings exits with an actionable error before API calls. The pure merge smoke also preserved repeated text, timestamp ties, and null text without credentials.
- The environment was upgraded from macOS system Python 3.9.6/LibreSSL to uv-managed CPython 3.13.9 with OpenSSL 3.5.4. `make sync`, all five tests, and credential-free CLI help passed under 3.13 without the old urllib3 SSL warning. Do not downgrade to the system Python to recreate the environment.

## Module boundaries

- `wlu/__main__.py`: stdlib `argparse`, startup configuration, authenticated session lifetime, progress display, and fetch → merge → write orchestration.
- `wlu/config.py`: load and validate the two credential settings only when `load_config()` is called. Imports must not require credentials.
- `wlu/notion.py`: database/block pagination and block-to-text extraction. Pass the request session explicitly; no global credential state.
- `wlu/merge.py`: pure daily DataFrame transformation, importable and usable without credentials. Preserve the daily-entry contract above.
- `nbs/`: model-training experiments, separate from application code.

No client classes, service/repository layers, or new framework are needed.
