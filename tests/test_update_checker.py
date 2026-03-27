from __future__ import annotations

import unittest

from elpx_translator_desktop.update_checker import (
    is_newer_version,
    is_prerelease_version,
    normalize_version,
    select_update_release,
)


class UpdateCheckerTests(unittest.TestCase):
    def test_prerelease_detection(self) -> None:
        self.assertTrue(is_prerelease_version('0.1.5b5'))
        self.assertTrue(is_prerelease_version('0.1.7~beta1'))
        self.assertTrue(is_prerelease_version('v0.1.5rc1'))
        self.assertFalse(is_prerelease_version('0.1.5'))

    def test_version_normalization_orders_stable_after_beta(self) -> None:
        self.assertGreater(normalize_version('0.1.5'), normalize_version('0.1.5b5'))
        self.assertGreater(normalize_version('0.1.5rc1'), normalize_version('0.1.5b5'))
        self.assertGreater(normalize_version('0.1.6b1'), normalize_version('0.1.5'))

    def test_is_newer_version_handles_beta_numbers(self) -> None:
        self.assertTrue(is_newer_version('0.1.5b6', '0.1.5b5'))
        self.assertFalse(is_newer_version('0.1.5b4', '0.1.5b5'))
        self.assertTrue(is_newer_version('0.1.7', '0.1.7~beta1'))
        self.assertTrue(is_newer_version('v0.1.7-beta5', '0.1.7b4'))

    def test_stable_install_ignores_prereleases(self) -> None:
        releases = [
            {'tag_name': 'v0.1.6b1', 'html_url': 'https://example.test/beta', 'prerelease': True, 'draft': False},
            {'tag_name': 'v0.1.5', 'html_url': 'https://example.test/stable', 'prerelease': False, 'draft': False},
        ]

        selected = select_update_release(releases, '0.1.4')

        self.assertIsNotNone(selected)
        self.assertEqual(selected['version'], 'v0.1.5')

    def test_stable_install_can_opt_in_to_prereleases(self) -> None:
        releases = [
            {'tag_name': 'v0.1.7~beta1', 'html_url': 'https://example.test/beta71', 'prerelease': True, 'draft': False},
            {'tag_name': 'v0.1.6', 'html_url': 'https://example.test/stable', 'prerelease': False, 'draft': False},
        ]

        selected = select_update_release(releases, '0.1.6', allow_prereleases=True)

        self.assertIsNotNone(selected)
        self.assertEqual(selected['version'], 'v0.1.7~beta1')

    def test_beta_install_can_see_newer_prereleases(self) -> None:
        releases = [
            {'tag_name': 'v0.1.5b6', 'html_url': 'https://example.test/beta6', 'prerelease': True, 'draft': False},
            {'tag_name': 'v0.1.5', 'html_url': 'https://example.test/stable', 'prerelease': False, 'draft': False},
        ]

        selected = select_update_release(releases, '0.1.5b5')

        self.assertIsNotNone(selected)
        self.assertEqual(selected['version'], 'v0.1.5')

    def test_beta_install_can_see_future_beta_if_no_stable_exists(self) -> None:
        releases = [
            {'tag_name': 'v0.1.6b1', 'html_url': 'https://example.test/beta61', 'prerelease': True, 'draft': False},
            {'tag_name': 'v0.1.5b6', 'html_url': 'https://example.test/beta56', 'prerelease': True, 'draft': False},
        ]

        selected = select_update_release(releases, '0.1.5b5')

        self.assertIsNotNone(selected)
        self.assertEqual(selected['version'], 'v0.1.6b1')

    def test_beta_install_detects_newer_github_beta_tag_format(self) -> None:
        releases = [
            {'tag_name': 'v0.1.7-beta5', 'html_url': 'https://example.test/beta75', 'prerelease': True, 'draft': False},
            {'tag_name': 'v0.1.7-beta4', 'html_url': 'https://example.test/beta74', 'prerelease': True, 'draft': False},
        ]

        selected = select_update_release(releases, '0.1.7b4')

        self.assertIsNotNone(selected)
        self.assertEqual(selected['version'], 'v0.1.7-beta5')

    def test_ignores_drafts_and_older_versions(self) -> None:
        releases = [
            {'tag_name': 'v0.1.6', 'html_url': 'https://example.test/draft', 'prerelease': False, 'draft': True},
            {'tag_name': 'v0.1.5b4', 'html_url': 'https://example.test/old-beta', 'prerelease': True, 'draft': False},
        ]

        selected = select_update_release(releases, '0.1.5b5')

        self.assertIsNone(selected)


if __name__ == '__main__':
    unittest.main()
