#!/usr/bin/env python3
"""Quick script to check Cloud Run logs."""
import subprocess
import sys

service_name = "doc-summarizer-qa"
region = "us-central1"

print(f"Fetching logs for {service_name} in {region}...")
print()

try:
    result = subprocess.run(
        f"gcloud run services logs read {service_name} --region {region} --limit 50",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("❌ Failed to fetch logs")
        print(result.stderr)
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
