#!/usr/bin/env python3
"""Independent last-mile validation for the public static projection."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


OREAFONE_URL = re.compile(
    r"https?://(?:www\.)?github\.com/oreafone-labs/([A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)
LOCAL_PATH = re.compile(
    r"(?i)(?:[A-Z]:\\Users\\|file://(?:/[A-Z]:|/Users/|[A-Za-z0-9._~-]+/))"
)
SECRET_PATTERNS = (
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
TEXT_SUFFIXES = {
    ".html",
    ".htm",
    ".js",
    ".json",
    ".xml",
    ".txt",
    ".css",
    ".map",
    ".svg",
    ".webmanifest",
}
ALLOWED_REPOSITORY = "rra-docs-site"


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        for name in ("href", "src"):
            value = attributes.get(name)
            if value:
                self.targets.append(value)


def link_problems(site: Path, page: Path, text: str) -> list[str]:
    parser = LinkCollector()
    parser.feed(text)
    problems: list[str] = []
    for target in parser.targets:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        raw_path = unquote(parsed.path)
        candidate = site / raw_path.lstrip("/") if raw_path.startswith("/") else page.parent / raw_path
        if raw_path.endswith("/"):
            candidate = candidate / "index.html"
        if not candidate.resolve().exists():
            problems.append(f"missing link target {target} in {page}")
    return problems


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    site = root / "site"
    if not (site / "index.html").is_file():
        return ["site/index.html is missing"]
    metadata_path = site / "build-metadata.json"
    if not metadata_path.is_file():
        problems.append("site/build-metadata.json is missing")
    else:
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if not re.fullmatch(r"[0-9a-f]{40}", metadata.get("source_revision", "")):
                problems.append("build metadata has no full source revision")
            if metadata.get("authority") != "public_projection_only":
                problems.append("build metadata has an invalid authority marker")
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"invalid build metadata: {exc}")
    for path in site.rglob("*"):
        if path.is_symlink():
            problems.append(f"symbolic link is forbidden: {path}")
            continue
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in OREAFONE_URL.finditer(text):
            if match.group(1).lower() != ALLOWED_REPOSITORY:
                problems.append(f"private Oreafone repository URL in {path}")
        if LOCAL_PATH.search(text):
            problems.append(f"local machine path in {path}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                problems.append(f"credential-like value in {path}")
        if path.suffix.lower() in {".html", ".htm"}:
            problems.extend(link_problems(site, path, text))
    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    problems = validate(root)
    if problems:
        print("Public projection validation failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print("Public projection validation succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
