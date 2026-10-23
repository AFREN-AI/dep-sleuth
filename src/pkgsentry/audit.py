"""Risk scoring and public library functions."""

from __future__ import annotations

import urllib.error

from .manifest import parse_manifest
from .models import AuditFinding, Package, PackageEvidence
from .popular import POPULAR_NAMES
from .registry import fetch_metadata


def _edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, char_left in enumerate(left, start=1):
        current = [i]
        for j, char_right in enumerate(right, start=1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (char_left != char_right)))
        previous = current
    return previous[-1]


def _nearby(package: Package, max_distance: int = 2) -> tuple[str, ...]:
    names = POPULAR_NAMES.get(package.ecosystem.lower(), frozenset())
    name = package.name.lower().replace("_", "-")
    if name in names:
        return ()
    candidates = [candidate for candidate in names if abs(len(candidate) - len(name)) <= max_distance]
    ranked = sorted(((_edit_distance(name, candidate), candidate) for candidate in candidates))
    return tuple(candidate for distance, candidate in ranked if distance <= max_distance)[:3]


def _finding(package: Package, evidence: PackageEvidence, popular_names: tuple[str, ...] = ()) -> AuditFinding:
    reasons: list[str] = []
    if not evidence.exists:
        reasons.append("Package name was not found in its public registry")
        if popular_names:
            reasons.append("Name is close to a common package name: " + ", ".join(popular_names))
    else:
        if evidence.age_days is not None and evidence.age_days < 30:
            reasons.append("First published less than 30 days ago")
        if evidence.downloads is not None and evidence.downloads < 100:
            reasons.append(f"Fewer than 100 reported downloads in {evidence.download_window or 'the reported period'}")
        if evidence.maintainers is not None and evidence.maintainers <= 1:
            reasons.append("Registry metadata reports one or fewer maintainers")
        if popular_names:
            reasons.append("Name is close to a common package name: " + ", ".join(popular_names))
    if not evidence.exists:
        risk = "critical"
    elif popular_names or (evidence.age_days is not None and evidence.age_days < 30):
        risk = "high"
    elif reasons:
        risk = "review"
    else:
        risk = "low"
    return AuditFinding(package, evidence, risk, tuple(reasons), popular_names)


def check_package(package: Package) -> AuditFinding:
    """Check one package against its registry and return explainable evidence."""
    try:
        evidence = fetch_metadata(package)
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        evidence = PackageEvidence(exists=False, metadata_source=package.ecosystem.lower() + " registry")
    return _finding(package, evidence, _nearby(package))


def audit_packages(packages: list[Package]) -> list[AuditFinding]:
    """Check a sequence of npm/PyPI packages and return one finding per package."""
    return [check_package(package) for package in packages]


def audit_manifest(path: str) -> list[AuditFinding]:
    """Parse a supported manifest and check every direct dependency."""
    return audit_packages(parse_manifest(path))

