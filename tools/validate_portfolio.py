from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "REQUIREMENTS.md",
    "USE_CASES.md",
    "CHANGE_REQUEST_EXAMPLE.md",
    "BUSINESS_RULES.md",
    "DOMAIN_GLOSSARY.md",
    "ARCHITECTURE.md",
    "DIAGRAMS.md",
    "DATA_MODEL.md",
    "INTEGRATION_SCENARIOS.md",
    "API_CONTRACT.md",
    "API_EXAMPLES.md",
    "openapi.yaml",
    "SQL_EXAMPLES.md",
    "TEST_CASES.md",
    "TRACEABILITY.md",
    "DECISIONS.md",
    "INTERVIEW_GUIDE.md",
    "DEMO.md",
    "prototype/devwork_core.py",
    "prototype/test_devwork_core.py",
    "prototype/schema.sql",
]

FORBIDDEN_PATTERNS = {
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "IPv4 address": re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)"),
    "private key marker": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "production path": re.compile(r"(?<![A-Za-z0-9_])/(?:etc|opt|var|home|root)/[A-Za-z0-9_.\-/]+"),
    "secret assignment": re.compile(
        r"\b(?:token|secret|api[_-]?key|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{12,}",
        re.I,
    ),
}

LOCAL_LINK = re.compile(r"\[[^\]]+\]\((?!https?://|#|mailto:)([^)]+)\)")


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def validate_required_files() -> None:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        fail(f"missing required portfolio files: {', '.join(missing)}")


def validate_markdown_links() -> None:
    for file in ROOT.glob("*.md"):
        text = file.read_text(encoding="utf-8")
        for match in LOCAL_LINK.finditer(text):
            target = match.group(1).split("#", 1)[0]
            if not target:
                continue
            resolved = (file.parent / target).resolve()
            if not resolved.exists():
                fail(f"broken local link in {file.name}: {target}")


def validate_public_safety() -> None:
    candidates = list(ROOT.glob("*.md")) + list(ROOT.glob("*.yaml")) + list(ROOT.glob("*.yml"))
    candidates += list((ROOT / "prototype").glob("*"))
    for file in candidates:
        if not file.is_file():
            continue
        text = file.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_PATTERNS.items():
            match = pattern.search(text)
            if match:
                fail(f"{label} found in {file.relative_to(ROOT)}: {match.group(0)!r}")


def validate_mermaid_fences() -> None:
    for file in ROOT.glob("*.md"):
        text = file.read_text(encoding="utf-8")
        openings = text.count("```mermaid")
        fences = text.count("```")
        if openings and fences < openings * 2:
            fail(f"possibly unclosed Mermaid block in {file.name}")


def main() -> int:
    validate_required_files()
    validate_markdown_links()
    validate_public_safety()
    validate_mermaid_fences()
    print("DevWork public portfolio checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
