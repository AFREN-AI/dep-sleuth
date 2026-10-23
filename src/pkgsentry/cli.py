"""Command line entry point."""

from __future__ import annotations

import argparse
import json
import sys

from .audit import audit_manifest, check_package
from .models import Package


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pkg-sentry", description="Check dependency metadata before installation.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit", help="Check dependencies in package.json, requirements.txt, or pyproject.toml")
    audit.add_argument("manifest")
    audit.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    check = subparsers.add_parser("check", help="Check one npm or PyPI package")
    check.add_argument("ecosystem", choices=("npm", "pypi"))
    check.add_argument("name")
    check.add_argument("--version")
    check.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        findings = audit_manifest(args.manifest) if args.command == "audit" else [check_package(Package(args.ecosystem, args.name, args.version))]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"pkg-sentry: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps([finding.to_dict() for finding in findings], indent=2))
    else:
        for finding in findings:
            version = f" ({finding.package.version})" if finding.package.version else ""
            print(f"{finding.risk.upper():8} {finding.package.ecosystem}:{finding.package.name}{version}")
            for reason in finding.reasons:
                print(f"         - {reason}")
            evidence = finding.evidence
            details = []
            if evidence.age_days is not None:
                details.append(f"age {evidence.age_days}d")
            if evidence.downloads is not None:
                details.append(f"downloads/{evidence.download_window or 'period'} {evidence.downloads}")
            if details:
                print("         " + ", ".join(details))
    return 1 if any(item.risk == "critical" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

