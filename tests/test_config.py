import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from wlu.config import load_config


class ConfigTests(unittest.TestCase):
    def test_loads_project_dotenv_and_prefers_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "wlu"
            package.mkdir()
            (package / "__init__.py").touch()
            shutil.copyfile(Path(__file__).resolve().parents[1] / "wlu" / "config.py", package / "config.py")
            (root / ".env").write_text("NOTION_TOKEN=test-token\nNOTION_DATABASE_ID=test-database\n")
            environment = os.environ.copy()
            for key in ("NOTION_TOKEN", "NOTION_DATABASE_ID", "PYTHON_DOTENV_DISABLED"):
                environment.pop(key, None)
            environment["PYTHONPATH"] = str(root)
            other_directory = root / "other"
            other_directory.mkdir()
            check = (
                "import os; import wlu.config; "
                "assert 'NOTION_DATABASE_ID' not in os.environ; "
                "assert wlu.config.load_config() == ('test-token', 'test-database')"
            )
            subprocess.run([sys.executable, "-c", check], cwd=other_directory, env=environment, check=True)

            environment["NOTION_TOKEN"] = "environment-token"
            check = check.replace("'test-token'", "'environment-token'")
            subprocess.run([sys.executable, "-c", check], cwd=other_directory, env=environment, check=True)

    def test_requires_credentials_at_load_time(self):
        with patch.dict(os.environ, {"PYTHON_DOTENV_DISABLED": "1"}, clear=True):
            with self.assertRaises(ValueError):
                load_config()


if __name__ == "__main__":
    unittest.main()
