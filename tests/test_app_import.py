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

    def test_app_icon_path_resolves_in_source_tree(self) -> None:
        from elpx_translator_desktop.app import _resolve_app_icon_path

        icon_path = _resolve_app_icon_path()

        self.assertIsNotNone(icon_path)
        assert icon_path is not None
        self.assertTrue(icon_path.exists())
        self.assertEqual(icon_path.name, 'elpx-translator-desktop.svg')


if __name__ == '__main__':
    unittest.main()
