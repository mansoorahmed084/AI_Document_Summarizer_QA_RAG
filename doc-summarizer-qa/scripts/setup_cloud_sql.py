#!/usr/bin/env python3
"""
Cloud SQL setup script for Cloud Run deployment.

This script:
1. Creates a Cloud SQL PostgreSQL instance
2. Creates a database
3. Creates a database user
4. Grants Cloud Run service account access
5. Configures Cloud Run service with database connection
"""
import subprocess
import sys
import os
import secrets
import string


def run_command(cmd, check=True, capture_output=False, timeout=30):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,  # Always capture to get stderr
            text=True,
            timeout=timeout
        )
        if capture_output:
            # Return full result object if caller wants to check returncode/stderr
            # Otherwise return just stdout for convenience
            return result
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
        # Return a result-like object with returncode and stderr
        class ErrorResult:
            def __init__(self, returncode, stderr, stdout):
                self.returncode = returncode
                self.stderr = stderr
                self.stdout = stdout
        return ErrorResult(e.returncode, e.stderr or '', e.stdout or '')


def check_command_exists(cmd):
    """Check if a command exists."""
    try:
        subprocess.run(
            f"which {cmd}" if os.name != 'nt' else f"where {cmd}",
            shell=True,
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def generate_password(length=32):
    """Generate a secure random password (safe for shell commands)."""
    # Use characters that are safe for shell commands (avoid: * & ^ # $ ` | \ " ')
    # Keep it secure but shell-safe
    alphabet = string.ascii_letters + string.digits + "!@%+=-_"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    """Main setup function."""
    print("=" * 60)
    print("🗄️  Cloud SQL Setup for Cloud Run")
    print("=" * 60)
    print()

    # Check if gcloud is installed
    if not check_command_exists("gcloud"):
        print("❌ gcloud CLI is not installed. Please install it first.")
        print("   https://cloud.google.com/sdk/docs/install")
        sys.exit(1)

    # Get project ID
    project_result = run_command("gcloud config get-value project", capture_output=True)
    project_id = project_result.stdout.strip() if hasattr(project_result, 'stdout') else str(project_result)
    if not project_id:
        print("❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID")
        sys.exit(1)

    print(f"📦 Project: {project_id}")
    print()

    # Configuration
    region = "us-central1"
    instance_name = "doc-summarizer-db"
    db_name = "docsummarizer"
    db_user = "appuser"
    service_name = "doc-summarizer-qa"
    database_version = "POSTGRES_15"
    tier = "db-f1-micro"  # Change to db-g1-small for production

    # Check if instance already exists (optional - can skip if hanging)
    print(f"🔍 Checking if Cloud SQL instance '{instance_name}' exists...")
    print("   (Press Ctrl+C to skip check and proceed)")
    
    instance_exists = False
    connection_name = None
    
    # Ask user if they want to check (since it might hang)
    skip_check = input("   Skip instance check? (y/N): ").strip().lower()
    
    if skip_check != 'y':
        try:
            # Use list with filter instead of describe - usually faster
            print("   Checking... (timeout: 5s)")
            result = run_command(
                f"gcloud sql instances list --filter='name:{instance_name}' --format='value(name)'",
                check=False,
                capture_output=True,
                timeout=5
            )
            instance_exists = (result.returncode == 0 and result.stdout.strip() == instance_name)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            print("⚠️  Check timed out or cancelled")
            print("   Will assume instance doesn't exist and create a new one")
            instance_exists = False
        except Exception as e:
            print(f"⚠️  Could not check instance status: {e}")
            print("   Will assume instance does not exist")
            instance_exists = False
    else:
        print("   Skipping check - will assume instance doesn't exist")
        instance_exists = False

    if instance_exists:
        print(f"✅ Instance '{instance_name}' already exists")
        use_existing = input("   Use existing instance? (y/N): ").strip().lower()
        if use_existing != 'y':
            print("❌ Setup cancelled")
            sys.exit(0)
        
        # Get connection name
        try:
            conn_result = run_command(
                f'gcloud sql instances describe {instance_name} --format="value(connectionName)"',
                capture_output=True,
                timeout=10
            )
            connection_name = conn_result.stdout.strip() if hasattr(conn_result, 'stdout') else str(conn_result)
            print(f"✅ Connection name: {connection_name}")
        except Exception as e:
            print(f"⚠️  Could not get connection name: {e}")
            print("   You'll need to provide it manually")
            connection_name = input(f"   Enter connection name (PROJECT:REGION:INSTANCE): ").strip()
            if not connection_name:
                print("❌ Connection name is required")
                sys.exit(1)
    else:
        # Generate passwords
        root_password = generate_password()
        user_password = generate_password()
        
        print(f"🔐 Generated secure passwords")
        print(f"   Root password: {root_password[:8]}...")
        print(f"   User password: {user_password[:8]}...")
        print()
        
        confirm = input("Continue with Cloud SQL setup? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Setup cancelled")
            sys.exit(0)
        
        # Step 1: Create Cloud SQL instance
        print()
        print("=" * 60)
        print("Step 1: Creating Cloud SQL instance...")
        print("=" * 60)
        print(f"   Instance: {instance_name}")
        print(f"   Region: {region}")
        print(f"   Tier: {tier}")
        print(f"   Version: {database_version}")
        print()
        print("⏳ This may take 5-10 minutes...")
        print("   (Please be patient - Cloud SQL instance creation takes time)")
        
        # Instance creation can take 5-10 minutes, so use a longer timeout
        instance_created = False
        try:
            # Quote password to handle special characters safely
            result = run_command(
                f'gcloud sql instances create {instance_name} '
                f'--database-version={database_version} '
                f'--tier={tier} '
                f'--region={region} '
                f'--root-password="{root_password}"',
                check=False,  # Don't fail immediately, check the error
                capture_output=True,
                timeout=600  # 10 minutes timeout
            )
            if result.returncode == 0:
                instance_created = True
            else:
                # Check if error is because instance already exists
                error_output = result.stderr if hasattr(result, 'stderr') and result.stderr else ''
                if not error_output and hasattr(result, 'stdout'):
                    error_output = result.stdout
                error_str = str(error_output).lower()
                if 'already exists' in error_str or 'conflict' in error_str:
                    print("⚠️  Instance already exists!")
                    use_existing = input("   Use existing instance? (y/N): ").strip().lower()
                    if use_existing == 'y':
                        instance_created = True
                        instance_exists = True  # Set flag to use existing instance path
                    else:
                        print("❌ Setup cancelled")
                        sys.exit(0)
                else:
                    # Some other error occurred
                    print(f"❌ Failed to create instance. Error: {error_output}")
                    sys.exit(1)
        except subprocess.TimeoutExpired:
            print("⚠️  Command timed out, but checking if instance was created...")
            # Check if instance exists even after timeout
            try:
                check_result = run_command(
                    f'gcloud sql instances describe {instance_name} --format="value(state)"',
                    check=False,
                    capture_output=True,
                    timeout=10
                )
                if check_result.returncode == 0:
                    state = check_result.stdout.strip()
                    if state in ['RUNNABLE', 'PENDING_CREATE']:
                        print(f"✅ Instance exists (state: {state}) - continuing...")
                        instance_created = True
                    else:
                        print(f"⚠️  Instance state: {state}")
            except Exception as e:
                print(f"⚠️  Could not verify instance: {e}")
        except subprocess.CalledProcessError as e:
            # Check if error is because instance already exists
            error_output = str(e.stderr) if hasattr(e, 'stderr') and e.stderr else str(e)
            if 'already exists' in error_output or 'conflict' in error_output.lower():
                print("⚠️  Instance already exists!")
                use_existing = input("   Use existing instance? (y/N): ").strip().lower()
                if use_existing == 'y':
                    instance_created = True
                    instance_exists = True  # Set flag to use existing instance path
                else:
                    print("❌ Setup cancelled")
                    sys.exit(0)
            else:
                print(f"❌ Failed to create instance: {e}")
                sys.exit(1)
        
        if not instance_created:
            print("❌ Failed to create instance. Please check manually.")
            sys.exit(1)
        
        print("✅ Cloud SQL instance created")
        print()
        
        # Step 2: Create database (check if exists first)
        print("=" * 60)
        print("Step 2: Creating database...")
        print("=" * 60)
        db_exists = run_command(
            f'gcloud sql databases describe {db_name} --instance={instance_name}',
            check=False,
            capture_output=True,
            timeout=10
        )
        
        if db_exists.returncode != 0:
            run_command(
                f'gcloud sql databases create {db_name} --instance={instance_name}',
                timeout=60  # Database creation is usually quick
            )
            print(f"✅ Database '{db_name}' created")
        else:
            print(f"✅ Database '{db_name}' already exists")
        print()
        
        # Step 3: Create database user (check if exists first)
        print("=" * 60)
        print("Step 3: Creating database user...")
        print("=" * 60)
        user_exists = run_command(
            f'gcloud sql users describe {db_user} --instance={instance_name}',
            check=False,
            capture_output=True,
            timeout=10
        )
        
        if user_exists.returncode != 0:
            # Quote password to handle special characters safely
            run_command(
                f'gcloud sql users create {db_user} '
                f'--instance={instance_name} '
                f'--password="{user_password}"',
                timeout=60  # User creation is usually quick
            )
            print(f"✅ User '{db_user}' created")
        else:
            print(f"✅ User '{db_user}' already exists")
            print("⚠️  Using existing user - you'll need to provide the password")
            user_password = input(f"   Enter password for existing user '{db_user}': ").strip()
            if not user_password:
                print("❌ Password is required")
                sys.exit(1)
        print()
        
        # Get connection name
        try:
            conn_result = run_command(
                f'gcloud sql instances describe {instance_name} --format="value(connectionName)"',
                capture_output=True,
                timeout=10
            )
            connection_name = conn_result.stdout.strip() if hasattr(conn_result, 'stdout') else str(conn_result)
            print(f"✅ Connection name: {connection_name}")
        except Exception as e:
            print(f"⚠️  Could not get connection name: {e}")
            print("   You'll need to provide it manually")
            connection_name = input(f"   Enter connection name (PROJECT:REGION:INSTANCE): ").strip()
            if not connection_name:
                print("❌ Connection name is required")
                sys.exit(1)
        print()
        
        # Save passwords (optional - user can save manually)
        print("=" * 60)
        print("📝 IMPORTANT: Save these credentials securely!")
        print("=" * 60)
        print(f"Root Password: {root_password}")
        print(f"User Password: {user_password}")
        print(f"Connection Name: {connection_name}")
        print()
        print("⚠️  These passwords will not be shown again!")
        print()

    # Step 4: Grant Cloud Run service account access
    print("=" * 60)
    print("Step 4: Granting Cloud Run access...")
    print("=" * 60)
    
    # Get Cloud Run service account
    sa_result = run_command(
        f'gcloud run services describe {service_name} --region {region} '
        f'--format="value(spec.template.spec.serviceAccountName)"',
        capture_output=True
    )
    service_account = sa_result.stdout.strip() if hasattr(sa_result, 'stdout') else str(sa_result)
    
    if not service_account:
        print(f"⚠️  Service '{service_name}' not found. Creating it first...")
        print("   (You may need to deploy the service first)")
        service_account = f"{project_id.replace('-', '')}-compute@developer.gserviceaccount.com"
        print(f"   Using default service account: {service_account}")
    
    print(f"   Service account: {service_account}")
    
    # Grant Cloud SQL Client role
    print("   Granting cloudsql.client role...")
    # Use double quotes for Windows compatibility
    run_command(
        f'gcloud projects add-iam-policy-binding {project_id} '
        f'--member="serviceAccount:{service_account}" '
        f'--role="roles/cloudsql.client"'
    )
    print("✅ Cloud Run service account has Cloud SQL access")
    print()

    # Step 5: Configure Cloud Run with database connection
    print("=" * 60)
    print("Step 5: Configuring Cloud Run service...")
    print("=" * 60)
    
    # Get user password if using existing instance
    if instance_exists:
        print("⚠️  Using existing instance - you need to provide the database user password")
        user_password = input(f"   Enter password for user '{db_user}': ").strip()
        if not user_password:
            print("❌ Password is required")
            sys.exit(1)
    
    # Build connection string (URL encode password to handle special characters)
    import urllib.parse
    encoded_password = urllib.parse.quote(user_password, safe='')
    database_url = (
        f"postgresql://{db_user}:{encoded_password}@/{db_name}"
        f"?host=/cloudsql/{connection_name}"
    )
    
    print(f"   Connection string: postgresql://{db_user}:***@/{db_name}?host=/cloudsql/{connection_name}")
    print()
    
    # Update Cloud Run service
    print("   Updating Cloud Run service...")
    # Use double quotes for Windows compatibility and escape properly
    update_cmd = (
        f'gcloud run services update {service_name} '
        f'--region {region} '
        f'--add-cloudsql-instances {connection_name} '
        f'--set-env-vars "DATABASE_URL={database_url}"'
    )
    
    run_command(update_cmd)
    print("✅ Cloud Run service updated with database connection")
    print()

    # Step 6: Initialize database tables
    print("=" * 60)
    print("Step 6: Database initialization")
    print("=" * 60)
    print("   Tables will be created automatically on first connection")
    print("   Or you can run: python scripts/init_db.py")
    print()

    # Summary
    print("=" * 60)
    print("✅ Cloud SQL setup complete!")
    print("=" * 60)
    print()
    print("📋 Summary:")
    print(f"   Instance: {instance_name}")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    print(f"   Connection: {connection_name}")
    print(f"   Cloud Run service: {service_name}")
    print()
    print("🧪 Test the connection:")
    # Get actual service URL
    try:
        url_result = run_command(
            f'gcloud run services describe {service_name} --region {region} --format="value(status.url)"',
            capture_output=True,
            timeout=10
        )
        service_url = url_result.stdout.strip() if hasattr(url_result, 'stdout') else str(url_result)
        if service_url:
            print(f"   Health: {service_url}/health")
            print(f"   API Docs: {service_url}/docs")
        else:
            print(f"   https://{service_name}-{project_id.replace('_', '-')}.{region}.run.app/health")
    except Exception:
        print(f"   https://{service_name}-{project_id.replace('_', '-')}.{region}.run.app/health")
    print()
    print("📚 Next steps:")
    print("   1. Wait a few minutes for Cloud SQL instance to be fully ready (if just created)")
    print("   2. Test document upload endpoint")
    print("   3. Check Cloud Run logs if there are any issues")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
