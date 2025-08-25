#!/usr/bin/env python3
"""
Smart script to update the core framework to the latest version with submodule support.

Usage:
    # Update from within the submodule directory
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


def find_study_directory(study_name=None, base_dir=None):
    """Find the study directory by name or current location."""
    # Auto-detect base directory if not provided
    if not base_dir:
        base_dir = str(Path.cwd().parent)
    
    if study_name:
        # Look for study by name in base directory
        study_path = Path(base_dir) / study_name.lower().replace(' ', '-')
        if study_path.exists():
            return study_path
    
    # Try to find study from current directory (we're in the submodule)
    # The study directory is the parent of the current directory
    study_path = Path.cwd().parent
    
    # Verify it's actually a study directory
    if (study_path / "study_config.json").exists() or (study_path / "api_wsgi.py").exists():
        return study_path
    
    # If study_name provided, try common locations
    if study_name:
        common_paths = [
            Path(base_dir) / study_name.lower().replace(' ', '-'),
            Path(base_dir) / study_name.replace(' ', '-'),
            Path(base_dir) / study_name,
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


def check_submodule_setup():
    """Check if we're in a properly set up submodule."""
    print("🔍 Checking submodule setup...")
    
    # Check if we're in the framework directory
    if not Path("study_framework_core").exists():
        print("❌ Error: study_framework_core not found!")
        print("Please ensure you're running this script from the ubiwell-study-backend-core directory")
        return False
    
    # Check if parent directory has .git (indicating it's a git repo)
    parent_dir = Path("..")
    if not (parent_dir / ".git").exists():
        print("⚠️  Warning: Parent directory is not a git repository")
        print("Consider initializing git in the parent directory for better version control")
    
    print("✅ Submodule setup validated")
    return True


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
    
    # Check submodule setup
    if not check_submodule_setup():
        sys.exit(1)
    
    # Pull latest changes from Git
    print("📥 Pulling latest changes from Git...")
    run_command("git pull origin main")
    
    # Update the core package in the study's environment
    print("📦 Updating core package...")
    update_command = f"{conda_path} run -n {env_name} pip install --upgrade -e ."
    run_command(update_command)
    
    # Install/update requirements to ensure all dependencies are available
    print("📦 Installing/updating requirements...")
    requirements_file = Path.cwd() / "requirements.txt"
    if requirements_file.exists():
        install_command = f"{conda_path} run -n {env_name} pip install -r {requirements_file}"
        run_command(install_command)
    else:
        print("⚠️  Warning: requirements.txt not found in core framework")
    
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
    print()
    print("💡 To update the submodule in the parent repository:")
    print(f"   cd {study_path}")
    print(f"   git add ubiwell-study-backend-core")
    print(f"   git commit -m 'Updated framework to latest version'")


def main():
    parser = argparse.ArgumentParser(description='Update core framework to latest version')
    parser.add_argument('--study-name', help='Name of the study to update')
    parser.add_argument('--study-path', help='Path to the study directory (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    print("Core Framework Update (Submodule Version)")
    print("=" * 40)
    
    # Find study directory
    if args.study_path:
        study_path = Path(args.study_path)
        if not study_path.exists():
            print(f"❌ Study path does not exist: {args.study_path}")
            sys.exit(1)
    else:
        # Auto-detect study directory (parent of current submodule directory)
        study_path = find_study_directory(args.study_name)
        if not study_path:
            print("❌ Could not find study directory!")
            print("💡 Options:")
            print("   1. Run from within the submodule directory")
            print("   2. Use --study-path to specify the exact path")
            print("   3. Use --study-name to search by name")
            sys.exit(1)
    
    print(f"🔍 Auto-detected study directory: {study_path}")
    
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
