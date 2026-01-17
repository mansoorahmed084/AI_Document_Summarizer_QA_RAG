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


def run_command(cmd, check=True, capture_output=False):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        if capture_output:
            return result.stdout.strip()
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"   Error: {e}")
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

    # Set variables
    service_name = "doc-summarizer-qa"
    region = "us-central1"
    image_name = f"gcr.io/{project_id}/{service_name}"

    # Check if Docker is installed (for local builds)
    use_docker = check_command_exists("docker")
    
    if use_docker:
        # Build Docker image
        print("🔨 Building Docker image...")
        run_command(f"docker build -t {image_name}:latest .")
        print("✅ Docker image built successfully")
        print()

        # Push to Container Registry
        print("📤 Pushing image to Container Registry...")
        run_command(f"docker push {image_name}:latest")
        print("✅ Image pushed successfully")
        print()
    else:
        # Use Cloud Build instead
        print("⚠️  Docker not found locally. Using Cloud Build...")
        print("🔨 Building and pushing with Cloud Build...")
        run_command(f"gcloud builds submit --tag {image_name}:latest .")
        print("✅ Image built and pushed successfully")
        print()

    # Check if service exists
    print("🔍 Checking if service exists...")
    service_exists = run_command(
        f"gcloud run services describe {service_name} --region {region}",
        check=False,
        capture_output=True
    )

    if service_exists.returncode == 0:
        print("   Updating existing service...")
        deploy_cmd = "update"
    else:
        print("   Creating new service...")
        deploy_cmd = "deploy"

    # Deploy to Cloud Run
    print("🚀 Deploying to Cloud Run...")
    deploy_command = (
        f"gcloud run services {deploy_cmd} {service_name} "
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
    service_url = run_command(
        f"gcloud run services describe {service_name} --region {region} --format 'value(status.url)'",
        capture_output=True
    )

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
