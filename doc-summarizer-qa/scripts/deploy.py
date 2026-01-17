#!/usr/bin/env python3
"""
Deployment script for Cloud Run.

This script builds a Docker image, pushes it to Google Container Registry,
and deploys it to Cloud Run.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True, capture_output=False, cwd=None, timeout=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True,
            cwd=cwd,  # Use specified working directory
            timeout=timeout  # Add timeout
        )
        if capture_output:
            return result.stdout.strip()
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
        sys.exit(1)


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


def main():
    """Main deployment function."""
    print("🚀 Deploying AI Document Summarizer & Q&A to Cloud Run")
    print()

    # Change to project root directory (where Dockerfile is located)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    print(f"📁 Working directory: {project_root}")
    print()

    # Check if gcloud is installed
    if not check_command_exists("gcloud"):
        print("❌ gcloud CLI is not installed. Please install it first.")
        print("   https://cloud.google.com/sdk/docs/install")
        sys.exit(1)

    # Get project ID
    project_id = run_command("gcloud config get-value project", capture_output=True)
    if not project_id:
        print("❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID")
        sys.exit(1)

    print(f"📦 Project: {project_id}")
    print()

    # Verify Dockerfile exists
    dockerfile_path = project_root / "Dockerfile"
    if not dockerfile_path.exists():
        print(f"❌ Dockerfile not found at {dockerfile_path}")
        print("   Please run this script from the project root or ensure Dockerfile exists")
        sys.exit(1)

    # Set variables
    service_name = "doc-summarizer-qa"
    region = "us-central1"
    image_name = f"gcr.io/{project_id}/{service_name}"

    # Check if Docker is installed (for local builds)
    use_docker = check_command_exists("docker")
    
    if use_docker:
        # Build Docker image
        print("🔨 Building Docker image...")
        print(f"   Working directory: {os.getcwd()}")
        run_command(f"docker build -t {image_name}:latest .", cwd=str(project_root))
        print("✅ Docker image built successfully")
        print()

        # Push to Container Registry
        print("📤 Pushing image to Container Registry...")
        run_command(f"docker push {image_name}:latest", cwd=str(project_root))
        print("✅ Image pushed successfully")
        print()
    else:
        # Use Cloud Build instead
        print("⚠️  Docker not found locally. Using Cloud Build...")
        print("🔨 Building and pushing with Cloud Build...")
        print(f"   Working directory: {os.getcwd()}")
        print(f"   Dockerfile exists: {dockerfile_path.exists()}")
        # Explicitly use project_root as working directory for Cloud Build
        run_command(f"gcloud builds submit --tag {image_name}:latest .", cwd=str(project_root))
        print("✅ Image built and pushed successfully")
        print()

    # Deploy to Cloud Run
    # Note: 'gcloud run deploy' automatically creates or updates the service
    # No need to check if service exists first
    print("🚀 Deploying to Cloud Run...")
    print("   (This will create the service if it doesn't exist, or update if it does)")
    deploy_command = (
        f"gcloud run deploy {service_name} "
        f"--image {image_name}:latest "
        f"--platform managed "
        f"--region {region} "
        f"--allow-unauthenticated "
        f"--memory 2Gi "
        f"--cpu 2 "
        f"--timeout 300 "
        f"--max-instances 10 "
        f"--min-instances 0 "
        f"--port 8080 "
        f"--set-env-vars GCP_PROJECT_ID={project_id},GCP_REGION={region}"
    )
    
    run_command(deploy_command)
    print("✅ Deployment successful")
    print()

    # Get service URL
    print("🔗 Getting service URL...")
    try:
        service_url = run_command(
            f'gcloud run services describe {service_name} --region {region} --format="value(status.url)"',
            capture_output=True
        )
    except Exception as e:
        # If we can't get the URL, try alternative method
        print(f"⚠️  Could not get service URL automatically: {e}")
        service_url = f"https://{service_name}-{project_id.replace('_', '-')}.{region}.run.app"
        print(f"   Using default URL format: {service_url}")

    print()
    print("=" * 60)
    print("✅ Deployment complete!")
    print("=" * 60)
    print(f"🌐 Service URL: {service_url}")
    print(f"📚 API Docs: {service_url}/docs")
    print(f"❤️  Health Check: {service_url}/health")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
