from __future__ import annotations

import argparse
from pathlib import Path

from action_pack.pipeline import process_file, process_text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Turn public-sector documents into action packs."
    )
    parser.add_argument(
        "input", nargs="?", help="Path to PDF/TXT/MD file. If omitted, reads stdin."
    )
    parser.add_argument("--out", default="action-pack.md", help="Markdown output path")
    parser.add_argument(
        "--no-ai", action="store_true", help="Use deterministic local fallback only"
    )
    args = parser.parse_args()

    if args.input:
        result = process_file(args.input, use_ai=not args.no_ai)
    else:
        import sys

        result = process_text(sys.stdin.read(), use_ai=not args.no_ai)

    out = Path(args.out)
    out.write_text(result.markdown, encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Title: {result.pack.title}")
    print(f"Urgency: {result.pack.urgency_score}/5")
    print(f"Validation: {'ok' if result.validation.ok else 'issues'}")
    for issue in result.validation.issues:
        print(f"Issue: {issue}")
    for warning in result.validation.warnings:
        print(f"Warning: {warning}")
    return 0 if result.validation.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
