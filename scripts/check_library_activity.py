from __future__ import annotations
import argparse
from pathlib import Path
from typing import List

from resume_builder.tools.package_activity import (
    parse_requirements,
    build_report,
)


def main():
    ap = argparse.ArgumentParser(description="Generate a dependency activity report using PyPI and GitHub")
    ap.add_argument("--requirements", default=str(Path("requirements.txt")), help="Path to requirements.txt")
    ap.add_argument("--packages", nargs="*", help="Optional explicit package names to check (overrides requirements)")
    ap.add_argument("--out", default="dependency_activity.md", help="Output Markdown file path")
    ap.add_argument("--months-active", type=int, default=12, help="Months threshold for Active status")
    ap.add_argument("--months-quiet", type=int, default=24, help="Months threshold for Quiet vs Abandoned")
    args = ap.parse_args()

    if args.packages:
        packages: List[str] = args.packages
    else:
        packages = parse_requirements(args.requirements)

    report = build_report(packages, months_active=args.months_active, months_quiet=args.months_quiet)
    out_path = Path(args.out)
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote report: {out_path}")


if __name__ == "__main__":
    main()
