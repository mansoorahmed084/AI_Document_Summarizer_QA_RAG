#!/usr/bin/env python3
"""
Authorize your current IP address to access Cloud SQL.
"""
import subprocess
import sys
import urllib.request


def get_public_ip():
    """Get current public IP address."""
    try:
        response = urllib.request.urlopen('https://api.ipify.org', timeout=5)
        return response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"⚠️  Could not get public IP: {e}")
        return None


def main():
    """Authorize IP for Cloud SQL access."""
    print("=" * 60)
    print("🔐 Authorize IP for Cloud SQL Access")
    print("=" * 60)
    print()
    
    instance_name = "doc-summarizer-db"
    
    # Get current IP
    current_ip = get_public_ip()
    if not current_ip:
        print("❌ Could not determine your public IP")
        print("   Please enter it manually")
        current_ip = input("   Enter your public IP address: ").strip()
        if not current_ip:
            print("❌ IP address required")
            sys.exit(1)
    
    print(f"📍 Your public IP: {current_ip}")
    print()
    
    confirm = input(f"Authorize {current_ip}/32 for Cloud SQL access? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    print()
    print("🔧 Authorizing IP...")
    print("   This may take 1-2 minutes (Cloud SQL instance update)...")
    print()
    
    try:
        # Run with timeout and show output in real-time
        process = subprocess.Popen(
            f'gcloud sql instances patch {instance_name} '
            f'--authorized-networks={current_ip}/32',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Show output in real-time
        for line in process.stdout:
            print(f"   {line.rstrip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print()
            print("✅ IP address authorized successfully!")
            print()
            print("⏳ Wait 10-30 seconds for changes to propagate...")
            print()
        else:
            print()
            print(f"❌ Failed to authorize IP (exit code: {process.returncode})")
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print()
        print("⏱️  Command timed out, but it may still be processing...")
        print("   Check Cloud Console to verify if IP was authorized")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(1)
