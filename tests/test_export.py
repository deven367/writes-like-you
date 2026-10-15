import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
import requests

from wlu import __main__ as cli, notion
from wlu.merge import merge_entries


class ExportTests(unittest.TestCase):
    def test_export_merges_paginated_and_nested_text_in_chronological_order(self):
        def block(block_id, *texts, kind="paragraph", children=False):
            return {
                "id": block_id,
                "type": kind,
                "has_children": children,
                kind: {"rich_text": [{"plain_text": text} for text in texts]},
            }

        def page(page_id, timestamp):
            return {"id": page_id, "created_time": timestamp}

        def result(blocks, cursor=None):
            return {"results": blocks, "has_more": cursor is not None, "next_cursor": cursor}

        responses = {
            ("database", None): result([
                page("evening", "2024-01-02T18:00:00.000Z"),
                page("empty", "2024-01-04T08:00:00.000Z"),
            ], "next-database-page"),
            ("database", "next-database-page"): result([
                page("morning", "2024-01-02T08:00:00.000Z"),
                page("offset", "2024-01-03T00:30:00.000+01:00"),
            ]),
            ("evening", None): result([block("first", "Evening ", "entry.")], "next-block-page"),
            ("evening", "next-block-page"): result([
                block("parent", "A heading", kind="heading_2", children=True),
            ]),
            ("parent", None): result([block("nested", "Nested text.", kind="bulleted_list_item")]),
            ("empty", None): result([block("blank")]),
            ("morning", None): result([block("early", "Morning ", "entry.")]),
            ("offset", None): result([block("late", "Late entry.")]),
        }

        def request(method, url, **kwargs):
            if method == "POST":
                key = ("database", kwargs["json"].get("start_cursor"))
            else:
                key = (url.split("/")[-2], kwargs["params"].get("start_cursor"))
            response = unittest.mock.Mock()
            response.json.return_value = responses[key]
            return response

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "daily export.csv"
            with (
                patch.dict(os.environ, {"NOTION_TOKEN": "test-token", "NOTION_DATABASE_ID": "test-database", "PYTHON_DOTENV_DISABLED": "1"}),
                patch.object(cli.requests.Session, "request", side_effect=request),
                patch.object(notion.time, "sleep"),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                cli.main(["--output", str(output)])
            rows = pd.read_csv(output, keep_default_na=False)
            self.assertEqual(rows.to_dict("records"), [
                {
                    "id": "morning,evening,offset",
                    "ts": "2024-01-02 08:00:00+00:00",
                    "date": "2024-01-02",
                    "text": "Morning entry.\n\nEvening entry.\n\nA heading\n\nNested text.\n\nLate entry.",
                },
                {"id": "empty", "ts": "2024-01-04 08:00:00+00:00", "date": "2024-01-04", "text": ""},
            ])

    def test_api_failure_does_not_overwrite_existing_export(self):
        database = unittest.mock.Mock()
        database.json.return_value = {
            "results": [
                {"id": "first", "created_time": "2024-01-02T08:00:00.000Z"},
                {"id": "second", "created_time": "2024-01-02T18:00:00.000Z"},
            ],
            "has_more": False,
        }
        first = unittest.mock.Mock()
        first.json.return_value = {
            "results": [{"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "First entry."}]}}],
            "has_more": False,
        }
        failure = requests.Response()
        failure.status_code = 503

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "daily.csv"
            previous = b"previous complete export\n"
            output.write_bytes(previous)
            with (
                patch.dict(os.environ, {"NOTION_TOKEN": "test-token", "NOTION_DATABASE_ID": "test-database", "PYTHON_DOTENV_DISABLED": "1"}),
                patch.object(cli.requests.Session, "request", side_effect=[database, first, failure]),
                patch.object(notion.time, "sleep"),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(requests.HTTPError),
            ):
                cli.main(["--output", str(output)])
            self.assertEqual(output.read_bytes(), previous)

    def test_empty_database_exports_only_column_headers(self):
        empty = pd.DataFrame(columns=["id", "ts", "text"])
        self.assertEqual(merge_entries(empty).to_csv(index=False), "id,ts,date,text\n")


if __name__ == "__main__":
    unittest.main()
