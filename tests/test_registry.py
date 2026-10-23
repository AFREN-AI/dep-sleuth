import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from pkgsentry.models import Package, PackageEvidence
from pkgsentry.registry import fetch_metadata, package_exists


class FakeResponse:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return json.dumps(self.value).encode()


class RegistryTests(unittest.TestCase):
    @patch("pkgsentry.registry._get_json")
    def test_npm_metadata_includes_age_downloads_and_maintainers(self, get_json):
        get_json.side_effect = [
            {"time": {"created": "2020-01-01T00:00:00Z", "1.0.0": "2020-01-02T00:00:00Z"}, "dist-tags": {"latest": "1.0.0"}, "maintainers": [{"name": "a"}, {"name": "b"}]},
            {"downloads": 1234},
        ]
        result = fetch_metadata(Package("npm", "example"))
        self.assertTrue(result.exists)
        self.assertEqual(result.downloads, 1234)
        self.assertEqual(result.download_window, "last 365 days")
        self.assertEqual(result.maintainers, 2)

    @patch("pkgsentry.registry._get_json")
    def test_pypi_metadata_reports_monthly_download_window(self, get_json):
        get_json.side_effect = [
            {"info": {"version": "2.0", "author": "Maintainer"}, "releases": {"1.0": [{"upload_time_iso_8601": "2021-01-01T00:00:00Z"}]}},
            {"data": {"last_month": 56}},
        ]
        result = fetch_metadata(Package("pypi", "example"))
        self.assertEqual(result.downloads, 56)
        self.assertEqual(result.download_window, "last 30 days")
        self.assertEqual(result.maintainers, 1)

    @patch("pkgsentry.registry.fetch_metadata")
    def test_package_exists_returns_true_for_metadata(self, fetch):
        fetch.return_value = PackageEvidence(exists=True)
        self.assertTrue(package_exists(Package("npm", "example")))

    @patch("pkgsentry.registry.fetch_metadata")
    def test_package_exists_returns_false_for_404(self, fetch):
        fetch.side_effect = HTTPError("https://registry.invalid", 404, "missing", {}, None)
        self.assertFalse(package_exists(Package("npm", "missing")))

    @patch("pkgsentry.registry.fetch_metadata")
    def test_package_exists_propagates_non_404(self, fetch):
        fetch.side_effect = HTTPError("https://registry.invalid", 503, "unavailable", {}, None)
        with self.assertRaises(HTTPError):
            package_exists(Package("npm", "example"))


if __name__ == "__main__":
    unittest.main()
