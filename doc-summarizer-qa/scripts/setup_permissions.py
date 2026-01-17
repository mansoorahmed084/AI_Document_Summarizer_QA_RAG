#!/usr/bin/env python3
"""
Setup script to grant necessary IAM permissions for Cloud Build and Cloud Run.

This script grants the required permissions to your user account.
"""
import subprocess
import sys
import os


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return None


def main():
    """Main setup function."""
    print("🔐 Setting up IAM permissions for Cloud Build and Cloud Run")
    print()

    # Get project ID
    result = run_command("gcloud config get-value project", check=False)
    if not result or not result.stdout.strip():
        print("❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID")
        sys.exit(1)

    project_id = result.stdout.strip()
    print(f"📦 Project: {project_id}")
    print()

    # Get current user email
    result = run_command("gcloud config get-value account", check=False)
    if not result or not result.stdout.strip():
        print("❌ No account set. Run: gcloud auth login")
        sys.exit(1)

    user_email = result.stdout.strip()
    print(f"👤 User: {user_email}")
    print()

    # Required roles
    roles = [
        "roles/cloudbuild.builds.editor",  # Cloud Build Editor
        "roles/run.admin",                   # Cloud Run Admin
        "roles/iam.serviceAccountUser",    # Service Account User
        "roles/storage.admin",              # Storage Admin (for Container Registry)
    ]

    print("🔑 Granting IAM roles...")
    print()

    for role in roles:
        print(f"   Granting {role}...")
        cmd = (
            f"gcloud projects add-iam-policy-binding {project_id} "
            f"--member=user:{user_email} "
            f"--role={role}"
        )
        result = run_command(cmd, check=False)
        if result and result.returncode == 0:
            print(f"   ✅ {role} granted")
        else:
            print(f"   ⚠️  Failed to grant {role} (may already be granted)")
        print()

    print("=" * 60)
    print("✅ Permission setup complete!")
    print("=" * 60)
    print()
    print("You can now run the deployment script:")
    print("  python scripts/deploy.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
