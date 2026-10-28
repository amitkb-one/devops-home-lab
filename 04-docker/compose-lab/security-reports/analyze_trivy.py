import json
from collections import Counter

with open("trivy-distroless.json") as f:
    report = json.load(f)

findings = []

for result in report.get("Results", []):
    for v in result.get("Vulnerabilities", []) or []:
        if v.get("Severity") in ("HIGH", "CRITICAL"):
            findings.append({
                "target": result.get("Target"),
                "type": result.get("Type"),
                "package": v.get("PkgName"),
                "cve": v.get("VulnerabilityID"),
                "installed": v.get("InstalledVersion"),
                "fixed": v.get("FixedVersion") or "NO FIX",
                "severity": v.get("Severity")
            })

print(f"\nTotal findings: {len(findings)}")
print(f"Unique CVEs: {len(set(v['cve'] for v in findings))}")

print("\nFindings by type:")
for kind, count in Counter(v["type"] for v in findings).most_common():
    print(f"  {kind}: {count}")

print("\nTop affected packages:")
for package, count in Counter(v["package"] for v in findings).most_common():
    print(f"  {package}: {count}")

print("\nFindings with fixes available:")
for v in findings:
    if v["fixed"] != "NO FIX":
        print(
            f"{v['cve']} | {v['package']} | "
            f"{v['installed']} -> {v['fixed']}"
        )

print("\nFindings without listed fixes:")
for v in findings:
    if v["fixed"] == "NO FIX":
        print(f"{v['cve']} | {v['package']} | {v['installed']}")
