import unittest
from unittest.mock import patch

from pkgsentry.audit import audit_packages, check_package
from pkgsentry.models import AuditFinding, Package, PackageEvidence


class AuditTests(unittest.TestCase):
    @patch("pkgsentry.audit.fetch_metadata")
    def test_missing_package_is_critical(self, fetch):
        fetch.return_value = PackageEvidence(exists=False)
        result = check_package(Package("npm", "made-up-package-name"))
        self.assertEqual(result.risk, "critical")
        self.assertFalse(result.evidence.exists)

    @patch("pkgsentry.audit.fetch_metadata")
    def test_new_package_is_high_risk(self, fetch):
        fetch.return_value = PackageEvidence(exists=True, age_days=2, maintainers=3)
        result = check_package(Package("pypi", "fresh-package"))
        self.assertEqual(result.risk, "high")
        self.assertIn("First published less than 30 days ago", result.reasons)

    @patch("pkgsentry.audit.fetch_metadata")
    def test_typo_of_common_package_is_high_risk(self, fetch):
        fetch.return_value = PackageEvidence(exists=True, age_days=2000, downloads=10000, maintainers=4)
        result = check_package(Package("npm", "lodahs"))
        self.assertEqual(result.risk, "high")
        self.assertIn("lodash", result.similar_popular_names)

    @patch("pkgsentry.audit.fetch_metadata")
    def test_batch_returns_one_finding_per_package(self, fetch):
        fetch.return_value = PackageEvidence(exists=True, age_days=1000, downloads=20000, maintainers=4)
        results = audit_packages([Package("npm", "react"), Package("pypi", "requests")])
        self.assertEqual(len(results), 2)
        self.assertTrue(all(result.risk == "low" for result in results))

    def test_finding_serializes_for_json(self):
        finding = AuditFinding(Package("npm", "example"), PackageEvidence(exists=True), "low")
        self.assertEqual(finding.to_dict()["package"]["name"], "example")


if __name__ == "__main__":
    unittest.main()
