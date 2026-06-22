#!/usr/bin/env python3
"""Enforce the two golden rules on test files: no asserts, no locators.

Tests must read as workflows — assertions and selectors belong in page objects. This catches
the common violations before they're committed. It is intentionally simple (line scanning),
not a full parser; a `# noqa: test-rules` comment on a line opts that line out.

Run:  python scripts/check_test_rules.py [path ...]   (defaults to app_tests/tests)
Exit: 0 when clean, 1 (with a report) when a rule is broken.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGET = ROOT / "app_tests" / "tests"

# Patterns that must not appear inside a test file body.
FORBIDDEN = [
    (re.compile(r"^\s*assert\b"), "bare 'assert' (assertions belong in page-object verify_* methods)"),
    (re.compile(r"\.locator\("), "Playwright .locator() call (selectors belong in page objects)"),
    (re.compile(r"\.get_by_(text|role|label|placeholder|test_id)\("), "get_by_* locator (belongs in page objects)"),
    (re.compile(r"\bpage\.(click|fill|press|type|check|hover)\("), "raw page action (wrap it in a page-object method)"),
    (re.compile(r"\bquery_selector\("), "query_selector (belongs in page objects)"),
    (re.compile(r"^\s*(from|import)\s.*\bexpect\b"), "importing 'expect' (assertions belong in page objects)"),
]


def scan_file(path: Path) -> list[str]:
    problems = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "# noqa: test-rules" in line:
            continue
        for pattern, message in FORBIDDEN:
            if pattern.search(line):
                rel = path.relative_to(ROOT)
                problems.append(f"{rel}:{lineno}: {message}\n      {line.strip()}")
    return problems


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv] or [DEFAULT_TARGET]
    files: list[Path] = []
    for t in targets:
        t = t if t.is_absolute() else (ROOT / t)
        if t.is_dir():
            files.extend(sorted(t.rglob("test_*.py")))
        elif t.name.startswith("test_") and t.suffix == ".py":
            files.append(t)

    all_problems = []
    for f in files:
        all_problems.extend(scan_file(f))

    if all_problems:
        print("Test-rule check FAILED:\n")
        for p in all_problems:
            print(f"  - {p}")
        print("\nMove the flagged logic into a page-object method, or add '# noqa: test-rules' "
              "to a line that is a genuine, reviewed exception.")
        return 1
    print(f"Test-rule check passed — scanned {len(files)} test file(s), no asserts/locators in tests.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
