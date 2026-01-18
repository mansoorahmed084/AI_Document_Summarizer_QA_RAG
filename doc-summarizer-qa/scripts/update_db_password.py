#!/usr/bin/env python3
"""
Update database password in Cloud Run service.

Use this if the password in Cloud Run doesn't match the actual database user password.
"""
import subprocess
import sys
import urllib.parse


def run_command(cmd, check=True, capture_output=False, timeout=30):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"⏱️  Command timed out after {timeout} seconds: {cmd}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        elif e.stdout:
            print(f"   Output: {e.stdout}")
        else:
            print(f"   Exit code: {e.returncode}")
        if check:
            sys.exit(1)
        return e


def main():
    """Update database password in Cloud Run."""
    print("=" * 60)
    print("🔐 Update Database Password in Cloud Run")
    print("=" * 60)
    print()
    
    # Configuration
    project_result = run_command("gcloud config get-value project", capture_output=True)
    project_id = project_result.stdout.strip() if hasattr(project_result, 'stdout') else str(project_result)
    region = "us-central1"
    instance_name = "doc-summarizer-db"
    db_name = "docsummarizer"
    db_user = "appuser"
    service_name = "doc-summarizer-qa"
    
    print(f"📦 Project: {project_id}")
    print(f"📦 Instance: {instance_name}")
    print()
    
    # Get connection name
    print("🔍 Getting connection name...")
    conn_result = run_command(
        f'gcloud sql instances describe {instance_name} --format="value(connectionName)"',
        capture_output=True,
        timeout=10
    )
    connection_name = conn_result.stdout.strip() if hasattr(conn_result, 'stdout') else str(conn_result)
    print(f"✅ Connection name: {connection_name}")
    print()
    
    # Get current password
    print("⚠️  Enter the CORRECT password for the database user")
    print("   (This should match the password set in Cloud SQL)")
    user_password = input(f"   Enter password for user '{db_user}': ").strip()
    if not user_password:
        print("❌ Password is required")
        sys.exit(1)
    
    # Build connection string (URL encode password)
    encoded_password = urllib.parse.quote(user_password, safe='')
    database_url = (
        f"postgresql://{db_user}:{encoded_password}@/{db_name}"
        f"?host=/cloudsql/{connection_name}"
    )
    
    print()
    print("🔧 Updating Cloud Run service with new password...")
    print(f"   Connection: postgresql://{db_user}:***@/{db_name}?host=/cloudsql/{connection_name}")
    
    # Update Cloud Run service
    run_command(
        f'gcloud run services update {service_name} '
        f'--region {region} '
        f'--set-env-vars "DATABASE_URL={database_url}"',
        timeout=120
    )
    
    print("✅ Cloud Run service updated with new password")
    print()
    print("⏳ Service will redeploy automatically...")
    print("   Wait a minute, then test your endpoints again")
    print()
    
    # Get service URL
    try:
        url_result = run_command(
            f'gcloud run services describe {service_name} --region {region} --format="value(status.url)"',
            capture_output=True,
            timeout=10
        )
        service_url = url_result.stdout.strip() if hasattr(url_result, 'stdout') else str(url_result)
        if service_url:
            print(f"🧪 Test: {service_url}/health")
    except Exception:
        pass
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
