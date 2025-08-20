#!/usr/bin/env python3
"""
Simple script to update the core framework to the latest version.

Usage:
    python update_core.py --study-name "My Study"
"""

import argparse
import subprocess
import sys
import os


def run_command(command, check=True):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, shell=True, check=check)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        if check:
            sys.exit(1)
        return False


def update_core_framework(study_name):
    """Update the core framework to the latest version."""
    env_name = f"{study_name.lower().replace(' ', '-')}-env"
    
    print(f"🔄 Updating core framework in {env_name}")
    
    # Pull latest changes from Git
    print("📥 Pulling latest changes from Git...")
    run_command("git pull origin main")
    
    # Update the core package
    print("📦 Updating core package...")
    run_command(f"conda run -n {env_name} pip install --upgrade -e .")
    
    print("✅ Core framework updated successfully!")
    print("💡 You may need to restart the services:")
    print(f"   sudo systemctl restart {study_name.lower().replace(' ', '-')}-api")
    print(f"   sudo systemctl restart {study_name.lower().replace(' ', '-')}-internal")
    print("💡 Check service status:")
    print(f"   sudo systemctl status {study_name.lower().replace(' ', '-')}-api")
    print(f"   sudo systemctl status {study_name.lower().replace(' ', '-')}-internal")


def main():
    parser = argparse.ArgumentParser(description='Update core framework to latest version')
    parser.add_argument('--study-name', required=True, help='Name of the study')
    
    args = parser.parse_args()
    
    print("Core Framework Update")
    print("=" * 30)
    print(f"Study: {args.study_name}")
    print()
    
    update_core_framework(args.study_name)


if __name__ == "__main__":
    main()
