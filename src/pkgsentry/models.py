"""Public data types returned by package checks."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Package:
    ecosystem: str
    name: str
    version: str | None = None


@dataclass(frozen=True)
class PackageEvidence:
    exists: bool
    latest_version: str | None = None
    first_release: str | None = None
    age_days: int | None = None
    downloads: int | None = None
    download_window: str | None = None
    maintainers: int | None = None
    metadata_source: str | None = None


@dataclass(frozen=True)
class AuditFinding:
    package: Package
    evidence: PackageEvidence
    risk: str
    reasons: tuple[str, ...] = field(default_factory=tuple)
    similar_popular_names: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)

