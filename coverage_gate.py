#!/usr/bin/env python3
"""Coverage quality gate helper for local hooks and CI pipelines."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


def read_current_coverage(coverage_xml_path: pathlib.Path) -> float:
    if not coverage_xml_path.exists():
        raise FileNotFoundError(f"Coverage report not found: {coverage_xml_path}")

    with coverage_xml_path.open("r") as f:
        f.readline()  # skip XML declaration
        root = f.readline()

    match = re.search(r'line-rate="([0-9.]+)"', root)
    if not match:
        raise ValueError(f"line-rate attribute not found in: {coverage_xml_path}")
    line_rate = match.group(1)

    return float(line_rate) * 100.0


def read_baseline(baseline_path: pathlib.Path) -> float:
    if not baseline_path.exists():
        raise ValueError(f"Baseline file not found: {baseline_path}")

    content = baseline_path.read_text(encoding="utf-8").strip()

    return float(content)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Coverage quality gate: compare current coverage against a stored baseline.",
    )
    parser.add_argument(
        "--coverage-xml",
        default="coverage.xml",
        metavar="PATH",
        help="Path to the coverage.xml report (default: coverage.xml)",
    )
    parser.add_argument(
        "--baseline",
        default=".coverage-baseline",
        metavar="PATH",
        help="Path to the baseline file (default: .coverage-baseline)",
    )
    args = parser.parse_args()

    coverage_xml_path = pathlib.Path(args.coverage_xml)
    baseline_path = pathlib.Path(args.baseline)

    try:
        current = read_current_coverage(coverage_xml_path)
        baseline = read_baseline(baseline_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[coverage-gate] ERROR: {exc}")
        return 1

    if current < baseline:
        print(f"[coverage-gate] FAIL: cobertura regrediu de atual {baseline:.2f}% para {current:.2f}%")
        return 1

    if current == baseline:
        print(f"[coverage-gate] OK: cobertura manteve-se igual (baseline {baseline:.2f}%).")
    else:
        print(f"[coverage-gate] SUCC: cobertura evoluiu de atual {baseline:.2f}% para {current:.2f}%")
        baseline_path.write_text(f"{current:.2f}\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
