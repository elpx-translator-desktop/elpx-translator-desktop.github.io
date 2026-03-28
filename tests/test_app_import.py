from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


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

    def test_migrates_legacy_qsettings_when_new_store_is_empty(self) -> None:
        from elpx_translator_desktop import app as app_module

        class FakeSettings:
            _store: dict[tuple[str, str], dict[str, object]] = {}

            def __init__(self, organization: str, application: str) -> None:
                self._key = (organization, application)
                FakeSettings._store.setdefault(self._key, {})

            def allKeys(self) -> list[str]:
                return list(FakeSettings._store[self._key].keys())

            def value(self, key: str):
                return FakeSettings._store[self._key].get(key)

            def setValue(self, key: str, value: object) -> None:
                FakeSettings._store[self._key][key] = value

            def sync(self) -> None:
                return None

        FakeSettings._store = {
            (app_module.LEGACY_SETTINGS_ORGANIZATION, app_module.SETTINGS_APPLICATION): {
                'ui_language': 'gl',
                'translation_provider': 'openai',
            },
        }

        with patch.object(app_module, 'QSettings', FakeSettings):
            settings = app_module._migrate_legacy_settings_if_needed()

        self.assertEqual(
            FakeSettings._store[(app_module.SETTINGS_ORGANIZATION, app_module.SETTINGS_APPLICATION)],
            FakeSettings._store[(app_module.LEGACY_SETTINGS_ORGANIZATION, app_module.SETTINGS_APPLICATION)],
        )
        self.assertEqual(settings.value('ui_language'), 'gl')
        self.assertEqual(settings.value('translation_provider'), 'openai')


if __name__ == '__main__':
    unittest.main()
