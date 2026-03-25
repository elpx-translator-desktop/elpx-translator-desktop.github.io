from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


class AppImportTests(unittest.TestCase):
    def test_app_module_can_be_loaded_without_package_context(self) -> None:
        app_path = Path(__file__).resolve().parents[1] / 'src' / 'elpx_translator_desktop' / 'app.py'
        spec = importlib.util.spec_from_file_location('app', app_path)

        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)

        module = importlib.util.module_from_spec(spec)
        sys.modules.pop('app', None)
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop('app', None)

        self.assertEqual(module.__name__, 'app')


if __name__ == '__main__':
    unittest.main()
