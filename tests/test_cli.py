import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pkgsentry.cli import main
from pkgsentry.models import AuditFinding, Package, PackageEvidence


class CliTests(unittest.TestCase):
    @patch("pkgsentry.cli.audit_manifest")
    def test_audit_supports_json_after_subcommand(self, audit_manifest):
        audit_manifest.return_value = [AuditFinding(Package("npm", "example"), PackageEvidence(exists=True), "low")]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.json"
            path.write_text("{}")
            self.assertEqual(main(["audit", str(path), "--json"]), 0)

    def test_invalid_manifest_returns_error_code(self):
        self.assertEqual(main(["audit", "does-not-exist.json"]), 2)


if __name__ == "__main__":
    unittest.main()
