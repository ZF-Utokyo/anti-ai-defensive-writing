#!/usr/bin/env python3
"""Check that the Skill and quick prompt retain the same core policy invariants."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = {
    "skill": ROOT / "skills" / "anti-ai-defensive-writing" / "SKILL.md",
    "clean-prompt": ROOT / "prompts" / "quick-prompt.txt",
    "audit-prompt": ROOT / "prompts" / "audit-prompt.txt",
    "full-manuscript-prompt": ROOT / "prompts" / "full-manuscript-prompt.txt",
}

INVARIANTS = {
    "strongest-supported-claim": r"strongest claim.{0,80}evidence supports",
    "no-invented-statistics": r"(?:never|do not) invent.{0,120}confidence interval",
    "source-rhetoric-is-not-fact": r"unsupported interpretations.{0,120}not facts",
    "no-new-em-dashes": r"do not add em\s+dashes",
    "integrity-pass": r"integrity pass",
}


def main() -> int:
    failures = []
    texts = {name: path.read_text(encoding="utf-8") for name, path in DOCUMENTS.items()}
    for invariant, pattern in INVARIANTS.items():
        for document, text in texts.items():
            if not re.search(pattern, text, re.I | re.S):
                failures.append(f"{invariant} missing from {document}")
    if failures:
        print("Policy sync check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Policy sync check passed: {len(INVARIANTS)} invariants in {len(DOCUMENTS)} documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
