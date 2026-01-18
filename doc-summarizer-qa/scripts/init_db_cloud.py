#!/usr/bin/env python3
"""
Initialize database tables in Cloud SQL.

This script connects to Cloud SQL and creates the necessary tables.
It uses the DATABASE_URL from Cloud Run service environment variables.
"""
import subprocess
import sys
import os
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
    """Initialize database tables in Cloud SQL."""
    print("=" * 60)
    print("🗄️  Initialize Cloud SQL Database Tables")
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
    
    # Get connection info
    print("🔍 Getting Cloud SQL instance information...")
    conn_result = run_command(
        f'gcloud sql instances describe {instance_name} --format="value(connectionName)"',
        capture_output=True,
        timeout=10
    )
    connection_name = conn_result.stdout.strip() if hasattr(conn_result, 'stdout') else str(conn_result)
    
    # Get public IP
    ip_result = run_command(
        f'gcloud sql instances describe {instance_name} --format="value(ipAddresses[0].ipAddress)"',
        capture_output=True,
        timeout=10
    )
    public_ip = ip_result.stdout.strip() if hasattr(ip_result, 'stdout') else None
    
    print(f"✅ Connection name: {connection_name}")
    if public_ip:
        print(f"✅ Public IP: {public_ip}")
    else:
        print("⚠️  Could not get public IP - instance may not have public IP enabled")
    print()
    
    # Check if we're on Windows or need to use public IP
    use_public_ip = os.name == 'nt' or not public_ip is None
    
    if use_public_ip and public_ip:
        print("📡 Using public IP connection (Windows/local environment)")
        print("   Note: Make sure your IP is authorized in Cloud SQL")
        print()
    else:
        print("📡 Using Unix socket connection (Cloud Run/GCP environment)")
        print()
    
    # Get password
    print("⚠️  Enter the database user password")
    user_password = input(f"   Enter password for user '{db_user}': ").strip()
    if not user_password:
        print("❌ Password is required")
        sys.exit(1)
    
    # Build connection string
    encoded_password = urllib.parse.quote(user_password, safe='')
    
    if use_public_ip and public_ip:
        # Use public IP for local/Windows connections
        database_url = (
            f"postgresql://{db_user}:{encoded_password}@{public_ip}:5432/{db_name}"
        )
        print(f"   Connecting to: {public_ip}:5432")
    else:
        # Use Unix socket for Cloud Run
        database_url = (
            f"postgresql://{db_user}:{encoded_password}@/{db_name}"
            f"?host=/cloudsql/{connection_name}"
        )
        print(f"   Connecting via Unix socket")
    
    print()
    print("🔧 Initializing database tables...")
    print("   This will create: documents, requests")
    print()
    
    # Set DATABASE_URL and run init script
    env = os.environ.copy()
    env['DATABASE_URL'] = database_url
    
    # Run the init_db script with the DATABASE_URL
    script_path = os.path.join(os.path.dirname(__file__), 'init_db.py')
    result = subprocess.run(
        [sys.executable, script_path],
        env=env,
        cwd=os.path.dirname(os.path.dirname(script_path))
    )
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print("✅ Database tables initialized successfully!")
        print("=" * 60)
        print()
        print("📋 Created tables:")
        print("   - documents (document metadata)")
        print("   - requests (request history)")
        print()
        print("🧪 You can now test document upload:")
        try:
            url_result = run_command(
                f'gcloud run services describe {service_name} --region {region} --format="value(status.url)"',
                capture_output=True,
                timeout=10
            )
            service_url = url_result.stdout.strip() if hasattr(url_result, 'stdout') else str(url_result)
            if service_url:
                print(f"   {service_url}/documents/upload")
        except Exception:
            pass
    else:
        print()
        print("❌ Failed to initialize database tables")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
