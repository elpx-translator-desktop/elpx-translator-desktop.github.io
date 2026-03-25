from __future__ import annotations

import unittest
from unittest.mock import patch

from elpx_translator_desktop.translator_engine import TranslationEngine


class TranslatorEngineTests(unittest.TestCase):
    @patch('elpx_translator_desktop.translator_engine.os.nice')
    def test_does_not_report_priority_change_for_normal_priority(self, mock_nice) -> None:
        self.assertFalse(TranslationEngine._lower_process_priority(0))
        mock_nice.assert_not_called()


if __name__ == '__main__':
    unittest.main()
