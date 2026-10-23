"""Read-only clients for public npm and PyPI metadata."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone

from .models import Package, PackageEvidence

_TIMEOUT_SECONDS = 8
_USER_AGENT = "pkg-sentry/0.1.0 (read-only dependency metadata checker)"


def _get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _as_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _age_days(release_date: date | None) -> int | None:
    if release_date is None:
        return None
    return max((datetime.now(timezone.utc).date() - release_date).days, 0)


def fetch_metadata(package: Package) -> PackageEvidence:
    """Fetch metadata only. No package is downloaded, installed, or executed."""
    ecosystem = package.ecosystem.lower()
    if ecosystem == "npm":
        encoded_name = urllib.parse.quote(package.name, safe="@")
        data = _get_json(f"https://registry.npmjs.org/{encoded_name}")
        releases = data.get("time", {})
        dates = [_as_date(v) for k, v in releases.items() if k != "created" and k != "modified"]
        dates = [d for d in dates if d is not None]
        latest = data.get("dist-tags", {}).get("latest")
        try:
            downloads = _get_json(
                "https://api.npmjs.org/downloads/point/last-year/" + urllib.parse.quote(package.name, safe="@")
            ).get("downloads")
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError):
            downloads = None
        return PackageEvidence(
            exists=True,
            latest_version=latest,
            first_release=min(dates).isoformat() if dates else None,
            age_days=_age_days(min(dates) if dates else None),
            downloads=downloads if isinstance(downloads, int) else None,
            download_window="last 365 days" if isinstance(downloads, int) else None,
            maintainers=len(data.get("maintainers", [])) or None,
            metadata_source="npm registry",
        )

    if ecosystem == "pypi":
        data = _get_json(f"https://pypi.org/pypi/{urllib.parse.quote(package.name, safe='')}/json")
        info = data.get("info", {})
        releases = data.get("releases", {})
        dates: list[date] = []
        for files in releases.values():
            for item in files:
                release_date = _as_date(item.get("upload_time_iso_8601"))
                if release_date:
                    dates.append(release_date)
        maintainer_count = 1 if info.get("maintainer") or info.get("author") else None
        try:
            stats = _get_json(
                f"https://pypistats.org/api/packages/{urllib.parse.quote(package.name, safe='')}/recent"
            )
            downloads = stats.get("data", {}).get("last_month")
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError):
            downloads = None
        earliest = min(dates) if dates else None
        return PackageEvidence(
            exists=True,
            latest_version=info.get("version"),
            first_release=earliest.isoformat() if earliest else None,
            age_days=_age_days(earliest),
            downloads=downloads if isinstance(downloads, int) else None,
            download_window="last 30 days" if isinstance(downloads, int) else None,
            maintainers=maintainer_count,
            metadata_source="PyPI; download counts from pypistats.org",
        )
    raise ValueError(f"Unsupported package ecosystem: {package.ecosystem}")


def package_exists(package: Package) -> bool:
    """Return false for a registry 404, and propagate other lookup failures."""
    try:
        fetch_metadata(package)
        return True
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise

