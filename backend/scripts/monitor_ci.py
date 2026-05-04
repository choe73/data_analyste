#!/usr/bin/env python3
"""
Monitor GitHub Actions CI/CD pipeline.
Checks workflow status, logs, and alerts on failures.
"""

import subprocess
import json
import sys
from datetime import datetime

def run_command(cmd):
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1


def check_workflow_status():
    """Check latest workflow run status."""
    print("\n" + "="*80)
    print("GITHUB ACTIONS CI/CD MONITOR")
    print("="*80 + "\n")

    # Get latest workflow runs
    cmd = (
        "gh run list "
        "--workflow=daily_collection.yml "
        "--limit=5 "
        "--json=status,conclusion,name,createdAt,updatedAt,url"
    )

    output, code = run_command(cmd)

    if code != 0:
        print("❌ Failed to fetch workflow status")
        print(f"Error: {output}")
        return False

    try:
        runs = json.loads(output)
    except:
        print("❌ Failed to parse workflow output")
        return False

    if not runs:
        print("⚠️  No workflow runs found")
        return False

    print(f"📊 Latest {len(runs)} workflow runs:\n")

    for i, run in enumerate(runs, 1):
        status = run.get("status", "unknown")
        conclusion = run.get("conclusion", "pending")
        created = run.get("createdAt", "")
        url = run.get("url", "")

        # Status emoji
        if conclusion == "success":
            emoji = "✅"
        elif conclusion == "failure":
            emoji = "❌"
        elif status == "in_progress":
            emoji = "⏳"
        else:
            emoji = "⚠️"

        print(f"{i}. {emoji} {conclusion.upper():10s} | {created[:10]} | {url}")

    # Check latest run
    latest = runs[0]
    if latest.get("conclusion") == "failure":
        print("\n" + "="*80)
        print("❌ LATEST RUN FAILED - Getting logs...")
        print("="*80 + "\n")

        # Get run ID from URL
        run_url = latest.get("url", "")
        if "/runs/" in run_url:
            run_id = run_url.split("/runs/")[1]
            get_logs(run_id)
            return False

    elif latest.get("conclusion") == "success":
        print("\n✅ Latest run PASSED")
        return True

    elif latest.get("status") == "in_progress":
        print("\n⏳ Latest run IN PROGRESS")
        return None

    return None


def get_logs(run_id):
    """Get logs for a specific run."""
    cmd = f"gh run view {run_id} --log"
    output, code = run_command(cmd)

    if code == 0:
        print(output[-2000:])  # Last 2000 chars
    else:
        print(f"Failed to get logs: {output}")


def check_secrets():
    """Check if DATABASE_URL secret is set."""
    print("\n" + "="*80)
    print("CHECKING SECRETS")
    print("="*80 + "\n")

    cmd = "gh secret list"
    output, code = run_command(cmd)

    if code != 0:
        print("❌ Failed to check secrets")
        return False

    if "DATABASE_URL" in output:
        print("✅ DATABASE_URL secret is set")
        return True
    else:
        print("❌ DATABASE_URL secret NOT found")
        return False


def main():
    print(f"\n🕐 Monitor started at {datetime.now().isoformat()}\n")

    # Check secrets first
    secrets_ok = check_secrets()

    if not secrets_ok:
        print("\n⚠️  DATABASE_URL secret is missing!")
        print("Add it with: gh secret set DATABASE_URL")
        sys.exit(1)

    # Check workflow status
    status = check_workflow_status()

    print("\n" + "="*80)
    if status is False:
        print("❌ CI/CD FAILED - Action required")
        sys.exit(1)
    elif status is True:
        print("✅ CI/CD PASSED")
        sys.exit(0)
    else:
        print("⏳ CI/CD IN PROGRESS - Check back later")
        sys.exit(0)


if __name__ == "__main__":
    main()
