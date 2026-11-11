#!/usr/bin/env python3
"""Fail when a Trivy JSON report contains CRITICAL findings."""

import json
import sys
from pathlib import Path


def check_report(report_path):
    report = json.loads(Path(report_path).read_text())

    if not isinstance(report, dict):
        raise ValueError("Invalid Trivy report")

    results = report.get("Results")

    if not isinstance(results, list):
        raise ValueError("Missing Trivy Results array")

    critical = []

    for result in results:
        for vuln in result.get("Vulnerabilities") or []:
            if vuln.get("Severity") == "CRITICAL":
                critical.append(vuln.get("VulnerabilityID"))

    if critical:
        print(f"SECURITY GATE FAILED: {len(critical)} CRITICAL findings")
        for cve in critical:
            print(f" - {cve}")
        return 1

    print("SECURITY GATE PASSED: No CRITICAL findings")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_trivy.py <report.json>")
        sys.exit(2)

    try:
        sys.exit(check_report(sys.argv[1]))
    except (OSError, ValueError, TypeError) as exc:
        print(f"SECURITY GATE ERROR: {exc}")
        sys.exit(2)
