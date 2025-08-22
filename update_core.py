#!/usr/bin/env python3
"""
Smart script to update the core framework to the latest version.

Usage:
    # Update from within a study directory
    python update_core.py
    
    # Update a specific study by name
    python update_core.py --study-name "My Study"
    
    # Update a study in a specific location
    python update_core.py --study-path "/path/to/my/study"
"""

import argparse
import subprocess
import sys
import os
import shutil
from pathlib import Path


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


def find_study_directory(study_name=None, base_dir="/mnt/study"):
    """Find the study directory by name or current location."""
    if study_name:
        # Look for study by name in base directory
        study_path = Path(base_dir) / study_name.lower().replace(' ', '-')
        if study_path.exists():
            return study_path
    
    # Try to find study from current directory
    current_path = Path.cwd()
    
    # Check if we're in a study directory (has study_config.json)
    if (current_path / "study_config.json").exists():
        return current_path
    
    # Check if we're in a subdirectory of a study
    for parent in current_path.parents:
        if (parent / "study_config.json").exists():
            return parent
    
    # If study_name provided, try common locations
    if study_name:
        common_paths = [
            Path(base_dir) / study_name.lower().replace(' ', '-'),
            Path(base_dir) / study_name.replace(' ', '-'),
            Path(base_dir) / study_name,
            Path("/tmp") / study_name.lower().replace(' ', '-'),
            Path("/tmp") / study_name.replace(' ', '-'),
            Path("/tmp") / study_name,
        ]
        
        for path in common_paths:
            if path.exists():
                return path
    
    return None


def get_conda_path(study_path):
    """Get conda path based on study location."""
    # Try to find conda in common locations
    conda_paths = [
        "/mnt/study/anaconda3/bin/conda",
        "/opt/anaconda3/bin/conda",
        "/usr/local/anaconda3/bin/conda",
        os.path.expanduser("~/anaconda3/bin/conda"),
    ]
    
    for conda_path in conda_paths:
        if os.path.exists(conda_path):
            return conda_path
    
    # Try to find conda in PATH
    try:
        result = subprocess.run(["which", "conda"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return "conda"  # Fallback to conda in PATH


def copy_core_framework(study_dir: Path, user: str):
    """Copy the core framework package to the study directory."""
    try:
        # Get the path to the core framework
        core_framework_dir = Path.cwd() / "study_framework_core"
        study_core_dir = study_dir / "study_framework_core"
        
        if core_framework_dir.exists():
            print(f"📦 Copying core framework to {study_core_dir}")
            
            # Remove existing core framework directory
            if study_core_dir.exists():
                shutil.rmtree(study_core_dir)
            
            # Copy the entire study_framework_core directory
            shutil.copytree(core_framework_dir, study_core_dir, dirs_exist_ok=True)
            
            # Make sure the package is properly set up
            init_file = study_core_dir / "__init__.py"
            if not init_file.exists():
                init_file.touch()
            
            # Set ownership to the study user
            run_command(f"chown -R {user}:{user} {study_core_dir}")
            
            print(f"✅ Core framework copied successfully")
        else:
            print(f"❌ Error: Core framework directory not found: {core_framework_dir}")
            
    except Exception as e:
        print(f"❌ Error copying core framework: {e}")
        raise


def get_env_name(study_path):
    """Get conda environment name from study path."""
    study_name = study_path.name
    return f"{study_name}-env"


def update_core_framework(study_path, study_name=None):
    """Update the core framework to the latest version."""
    if not study_path:
        print("❌ Could not find study directory!")
        print("💡 Try running from within a study directory or specify --study-path")
        sys.exit(1)
    
    study_path = Path(study_path)
    env_name = get_env_name(study_path)
    conda_path = get_conda_path(study_path)
    
    print(f"🔄 Updating core framework")
    print(f"📁 Study directory: {study_path}")
    print(f"🐍 Conda environment: {env_name}")
    print(f"📦 Conda path: {conda_path}")
    print()
    
    # Check if we're in the right directory (should be the core framework repo)
    if not (Path.cwd() / "study_framework_core").exists():
        print("❌ Error: This script should be run from the core framework repository!")
        print("💡 Please run from: /path/to/ubiwell-study-backend-core")
        sys.exit(1)
    
    # Pull latest changes from Git
    print("📥 Pulling latest changes from Git...")
    run_command("git pull origin main")
    
    # Update the core package in the study's environment (copy files, not editable)
    print("📦 Updating core package...")
    update_command = f"{conda_path} run -n {env_name} pip install --upgrade {Path.cwd()}/study_framework_core/"
    run_command(update_command)
    
    # Copy updated core framework files to study directory
    print("📁 Copying updated core framework files...")
    copy_core_framework(study_path, study_path.name)
    
    print("✅ Core framework updated successfully!")
    print()
    print("💡 You may need to restart the services:")
    service_name = study_path.name
    print(f"   sudo systemctl restart {service_name}-api")
    print(f"   sudo systemctl restart {service_name}-internal")
    print()
    print("💡 Check service status:")
    print(f"   sudo systemctl status {service_name}-api")
    print(f"   sudo systemctl status {service_name}-internal")
    print()
    print("💡 Test the update:")
    print(f"   cd {study_path}")
    print(f"   {conda_path} run -n {env_name} python -c \"from study_framework_core.core.config import get_config; print('✅ Update successful!')\"")


def main():
    parser = argparse.ArgumentParser(description='Update core framework to latest version')
    parser.add_argument('--study-name', help='Name of the study to update')
    parser.add_argument('--study-path', help='Path to the study directory')
    parser.add_argument('--base-dir', default='/mnt/study', help='Base directory for studies (default: /mnt/study)')
    
    args = parser.parse_args()
    
    print("Core Framework Update")
    print("=" * 30)
    
    # Find study directory
    if args.study_path:
        study_path = Path(args.study_path)
        if not study_path.exists():
            print(f"❌ Study path does not exist: {args.study_path}")
            sys.exit(1)
    else:
        study_path = find_study_directory(args.study_name, args.base_dir)
    
    if not study_path:
        print("❌ Could not find study directory!")
        print("💡 Options:")
        print("   1. Run from within a study directory")
        print("   2. Use --study-path to specify the exact path")
        print("   3. Use --study-name to search by name")
        sys.exit(1)
    
    print(f"Study: {study_path.name}")
    print(f"Path: {study_path}")
    print()
    
    update_core_framework(study_path, args.study_name)


if __name__ == "__main__":
    main()
