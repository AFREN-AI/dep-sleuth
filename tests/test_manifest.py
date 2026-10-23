import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from pkgsentry.manifest import parse_manifest
from pkgsentry.audit import audit_manifest
from pkgsentry.models import AuditFinding, PackageEvidence


class ManifestTests(unittest.TestCase):
    def test_package_json_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.json"
            path.write_text(json.dumps({"dependencies": {"express": "^4.0"}, "devDependencies": {"jest": "^30"}}))
            found = parse_manifest(path)
        self.assertEqual([(p.name, p.ecosystem) for p in found], [("express", "npm"), ("jest", "npm")])

    def test_requirements_ignores_comments_and_options(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requirements.txt"
            path.write_text("requests>=2.0 # HTTP\n-r extra.txt\nfastapi[standard]==1.0\n")
            found = parse_manifest(path)
        self.assertEqual([p.name for p in found], ["fastapi", "requests"])

    def test_pyproject_reads_optional_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pyproject.toml"
            path.write_text('[project]\ndependencies=["httpx>=0.1"]\n[project.optional-dependencies]\ndev=["pytest>=8"]\n')
            found = parse_manifest(path)
        self.assertEqual([p.name for p in found], ["httpx", "pytest"])

    def test_unsupported_file_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Pipfile"
            path.write_text("[packages]\nrequests='*'\n")
            with self.assertRaisesRegex(ValueError, "Supported files"):
                parse_manifest(path)

    @patch("pkgsentry.audit.check_package")
    def test_audit_manifest_checks_each_dependency(self, check):
        check.side_effect = lambda package: AuditFinding(package, PackageEvidence(exists=True), "low")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requirements.txt"
            path.write_text("requests\nhttpx\n")
            result = audit_manifest(str(path))
        self.assertEqual([finding.package.name for finding in result], ["httpx", "requests"])
        self.assertEqual(check.call_count, 2)


if __name__ == "__main__":
    unittest.main()
