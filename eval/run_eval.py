"""Run provenance-aware dependency cases against live registries."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pkgsentry.audit import check_package
from pkgsentry.models import Package

REQUIRED = {"id", "ecosystem", "package", "expectation", "basis", "model_id", "model_version", "sample_source", "collected_at"}


def main() -> int:
    cases = [json.loads(line) for line in Path(__file__).with_name("generated_dependencies.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    failed = 0
    groups: dict[tuple[str, str], list[tuple[bool | None, bool]]] = {}
    for case in cases:
        missing = REQUIRED - case.keys()
        if missing:
            raise ValueError(f"{case.get('id', '<unknown>')} missing provenance fields: {', '.join(sorted(missing))}")
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
        key = (case["model_id"], case["model_version"])
        expected_critical = {"must_be_critical": True, "must_not_be_critical": False, "warn_or_critical": None}[expectation]
        groups.setdefault(key, []).append((expected_critical, finding.risk == "critical"))
    print(f"smoke cases passing={len(cases) - failed}/{len(cases)}")
    for (model, version), outcomes in sorted(groups.items()):
        labeled = [(expected, actual) for expected, actual in outcomes if expected is not None]
        tp = sum(expected and actual for expected, actual in labeled)
        fp = sum(not expected and actual for expected, actual in labeled)
        fn = sum(expected and not actual for expected, actual in labeled)
        tn = sum(not expected and not actual for expected, actual in labeled)
        print(f"model={model}@{version} n={len(outcomes)} binary_labeled={len(labeled)} critical_tp={tp} critical_fp={fp} critical_fn={fn} noncritical_tn={tn}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
