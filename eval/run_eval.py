"""Run the illustrative generated-dependency cases against live registries."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pkgsentry.audit import check_package
from pkgsentry.models import Package


def main() -> int:
    cases = [json.loads(line) for line in Path(__file__).with_name("generated_dependencies.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    failed = 0
    for case in cases:
        finding = check_package(Package(case["ecosystem"], case["package"]))
        expectation = case["expectation"]
        passes = {
            "must_be_critical": finding.risk == "critical",
            "must_not_be_critical": finding.risk != "critical",
            "warn_or_critical": finding.risk in {"high", "critical"},
        }[expectation]
        if not passes:
            failed += 1
        print(f"{case['id']}: {'PASS' if passes else 'FAIL'} expectation={expectation} actual={finding.risk}")
    print(f"smoke cases passing={len(cases) - failed}/{len(cases)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
