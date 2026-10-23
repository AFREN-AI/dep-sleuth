"""Extract dependency names from common npm and Python project files."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from .models import Package

_REQ_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)")


def parse_manifest(path: str | Path) -> list[Package]:
    """Parse package.json, requirements.txt, or pyproject.toml dependencies."""
    source = Path(path)
    suffix = source.name.lower()
    text = source.read_text(encoding="utf-8")
    if suffix == "package.json":
        data = json.loads(text)
        found: dict[str, str | None] = {}
        for section in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
            for name, version in data.get(section, {}).items():
                found[name] = version if isinstance(version, str) else None
        return [Package("npm", name, version) for name, version in sorted(found.items())]
    if suffix == "requirements.txt" or suffix.endswith(".requirements.txt"):
        found = {}
        for line in text.splitlines():
            line = line.split("#", 1)[0].strip()
            match = _REQ_NAME.match(line)
            if match and not line.startswith(("-", "git+", "http:")):
                name = match.group(1)
                found[name] = line[len(name):].strip() or None
        return [Package("pypi", name, version) for name, version in sorted(found.items())]
    if suffix == "pyproject.toml":
        data = tomllib.loads(text)
        dependencies = list(data.get("project", {}).get("dependencies", []))
        optional = data.get("project", {}).get("optional-dependencies", {})
        for group in optional.values():
            dependencies.extend(group)
        found = {}
        for requirement in dependencies:
            match = _REQ_NAME.match(requirement)
            if match:
                name = match.group(1)
                found[name] = requirement[len(name):].strip() or None
        return [Package("pypi", name, version) for name, version in sorted(found.items())]
    raise ValueError("Supported files: package.json, requirements.txt, pyproject.toml")

