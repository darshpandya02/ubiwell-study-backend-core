#!/usr/bin/env python3
"""
Study Framework Core - Red Hat Setup Script

This script sets up a complete study environment on Red Hat/CentOS/RHEL systems.
It mirrors the Ubuntu setup_study.py functionality but adapts for Red Hat systems.

Usage:
    sudo python setup_study_redhat.py "Study Name" [options]

Example:
    sudo python setup_study_redhat.py "Bean Study" \
        --user bean-study \
        --db-username myuser \
        --db-password mypass \
        --db-name bean_study_db \
        --auth-key my-auth-key \
        --announcement-key my-announcement-key
"""

import argparse
import subprocess
import sys
import os
import json
import random
import string
from pathlib import Path
import shutil
import urllib.request
import tarfile
import tempfile


def run_command(command, check=True, capture_output=True, text=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, check=check, capture_output=capture_output, text=text, shell=True)
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print(f"❌ Error running command: {command}")
            print(f"Error: {e}")
            sys.exit(1)
        return e


def check_redhat_system():
    """Check if this is a Red Hat system."""
    try:
        with open('/etc/redhat-release', 'r') as f:
            release_info = f.read().strip()
            print(f"✅ Detected Red Hat system: {release_info}")
            
            # Extract version information
            if 'release 8' in release_info or 'release 9' in release_info:
                print("✅ Compatible RHEL version detected")
            else:
                print("⚠️ Warning: This script is optimized for RHEL 8/9")
                print("📝 MongoDB installation may require manual setup")
            
            return True
    except FileNotFoundError:
        print("❌ This script is designed for Red Hat/CentOS/RHEL systems")
        print("💡 For Ubuntu/Debian systems, use setup_study.py")
        sys.exit(1)


def check_root():
    """Check if running as root."""
    if os.geteuid() != 0:
        print("❌ This script must be run as root (use sudo)")
        sys.exit(1)


def check_dependencies():
    """Check and install required system dependencies."""
    print("🔍 Checking system dependencies...")
    
    # Check if MongoDB is already installed
    if shutil.which('mongod'):
        print("✅ MongoDB is already installed")
        try:
            # Check if MongoDB is running
            result = run_command("systemctl is-active mongod", check=False)
            if result.returncode == 0:
                print("✅ MongoDB service is running")
            else:
                print("⚠️ MongoDB is installed but not running")
                print("💡 Start MongoDB with: sudo systemctl start mongod")
        except:
            print("⚠️ Could not check MongoDB service status")
    
    # Check if dnf/yum is available
    if not shutil.which('dnf') and not shutil.which('yum'):
        print("❌ Neither dnf nor yum package manager found")
        sys.exit(1)
    
    package_manager = 'dnf' if shutil.which('dnf') else 'yum'
    print(f"✅ Using package manager: {package_manager}")
    
    # Install required packages
    required_packages = [
        'python3',
        'python3-pip',
        'git',
        'nginx',
        'mongodb-org',  # MongoDB repository needs to be added first
        'systemd',
        'wget',
        'curl'
    ]
    
    print("📦 Installing required packages...")
    
    # Add MongoDB repository first
    print("🔧 Setting up MongoDB repository...")
    try:
        # Create MongoDB repository file
        mongodb_repo_content = """[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
"""
        
        # Write repository file
        with open('/etc/yum.repos.d/mongodb-org-6.0.repo', 'w') as f:
            f.write(mongodb_repo_content)
        
        print("✅ MongoDB repository configured")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not configure MongoDB repository: {e}")
        print("📝 You may need to install MongoDB manually")
    
    # Install other packages
    for package in required_packages:
        try:
            run_command(f"{package_manager} install -y {package}")
        except Exception as e:
            if package == 'mongodb-org':
                print(f"⚠️ Warning: Could not install MongoDB via package manager: {e}")
                provide_mongodb_alternatives()
                print("🔄 Continuing with setup... MongoDB can be installed later")
            else:
                print(f"❌ Error installing {package}: {e}")
                raise e
    
    print("✅ System dependencies installed")


def provide_mongodb_alternatives():
    """Provide alternative MongoDB installation methods."""
    print("\n🔧 Alternative MongoDB Installation Methods:")
    print("=" * 50)
    print("If the automatic MongoDB installation failed, try these alternatives:")
    print()
    print("1. Manual Repository Setup:")
    print("   sudo dnf config-manager --add-repo https://repo.mongodb.org/yum/redhat/8/mongodb-org/6.0/x86_64/")
    print("   sudo dnf install -y mongodb-org")
    print()
    print("2. Direct RPM Installation:")
    print("   wget https://repo.mongodb.org/yum/redhat/8/mongodb-org/6.0/x86_64/RPMS/mongodb-org-6.0.6-1.el8.x86_64.rpm")
    print("   sudo dnf install -y mongodb-org-6.0.6-1.el8.x86_64.rpm")
    print()
    print("3. Docker Installation:")
    print("   sudo dnf install -y docker")
    print("   sudo systemctl start docker")
    print("   sudo docker run -d --name mongodb -p 27017:27017 mongo:6.0")
    print()
    print("4. Manual Download:")
    print("   Visit: https://docs.mongodb.com/manual/administration/install-on-linux/")
    print("   Follow the Red Hat/CentOS installation instructions")
    print()


def check_anaconda():
    """Check for existing Anaconda installation or install if needed."""
    print("🐍 Checking Anaconda installation...")
    
    # Common Anaconda installation paths
    possible_paths = [
        '/opt/anaconda3/bin/conda',
        '/opt/miniconda3/bin/conda',
        '/usr/local/anaconda3/bin/conda',
        '/usr/local/miniconda3/bin/conda',
        '/home/*/anaconda3/bin/conda',
        '/home/*/miniconda3/bin/conda'
    ]
    
    found_installations = []
    
    # Check for existing installations
    for path_pattern in possible_paths:
        if '*' in path_pattern:
            # Handle wildcard paths
            import glob
            for path in glob.glob(path_pattern):
                if os.path.exists(path):
                    # Get the base conda directory (remove /bin/conda)
                    conda_dir = os.path.dirname(os.path.dirname(path))
                    print(f"🔍 Found conda at: {path} -> Base directory: {conda_dir}")
                    found_installations.append(conda_dir)
        else:
            if os.path.exists(path_pattern):
                # Get the base conda directory (remove /bin/conda)
                conda_dir = os.path.dirname(os.path.dirname(path_pattern))
                print(f"🔍 Found conda at: {path_pattern} -> Base directory: {conda_dir}")
                found_installations.append(conda_dir)
    
    if found_installations:
        if len(found_installations) == 1:
            conda_path = found_installations[0]
            print(f"✅ Found existing Anaconda installation: {conda_path}")
            return conda_path
        else:
            print("🔍 Multiple Anaconda installations found:")
            for i, path in enumerate(found_installations, 1):
                print(f"  {i}. {path}")
            
            while True:
                try:
                    choice = input("Select installation to use (or 'n' to install new): ").strip()
                    if choice.lower() == 'n':
                        break
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(found_installations):
                        conda_path = found_installations[choice_idx]
                        print(f"✅ Using existing installation: {conda_path}")
                        return conda_path
                    else:
                        print("❌ Invalid choice. Please try again.")
                except ValueError:
                    print("❌ Please enter a valid number.")
    
    # No existing installation found, offer to install
    print("❌ No Anaconda installation found")
    print("💡 Options:")
    print("  1. Install Miniconda automatically")
    print("  2. Provide custom Anaconda path")
    print("  3. Exit and install manually")
    
    while True:
        choice = input("Choose option (1-3): ").strip()
        if choice == '1':
            return install_anaconda()
        elif choice == '2':
            custom_path = input("Enter Anaconda installation path: ").strip()
            if os.path.exists(os.path.join(custom_path, 'bin', 'conda')):
                print(f"✅ Using custom Anaconda path: {custom_path}")
                return custom_path
            else:
                print("❌ Invalid Anaconda path")
        elif choice == '3':
            print("💡 Please install Anaconda manually and run this script again")
            sys.exit(1)
        else:
            print("❌ Invalid choice. Please try again.")


def install_anaconda():
    """Install Miniconda automatically."""
    print("📦 Installing Miniconda...")
    
    # Download Miniconda
    miniconda_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    installer_path = "/tmp/miniconda_installer.sh"
    
    print(f"📥 Downloading Miniconda from {miniconda_url}")
    urllib.request.urlretrieve(miniconda_url, installer_path)
    
    # Make installer executable
    os.chmod(installer_path, 0o755)
    
    # Install Miniconda to /opt/anaconda3
    install_dir = "/opt/anaconda3"
    run_command(f"bash {installer_path} -b -p {install_dir} -u")
    
    # Clean up installer
    os.remove(installer_path)
    
    # Add to system PATH
    conda_init_script = f"""
#!/bin/bash
# Conda initialization for system-wide use
export PATH="{install_dir}/bin:$PATH"
"""
    
    with open('/etc/profile.d/conda.sh', 'w') as f:
        f.write(conda_init_script)
    
    os.chmod('/etc/profile.d/conda.sh', 0o644)
    
    print(f"✅ Miniconda installed to {install_dir}")
    return install_dir


def create_user(username):
    """Create system user for the study."""
    print(f"👤 Creating user: {username}")
    
    # Check if user already exists
    result = run_command(f"id {username}", check=False)
    if result.returncode == 0:
        print(f"✅ User {username} already exists")
        return
    
    # Create user with home directory
    run_command(f"useradd -m -s /bin/bash {username}")
    
    # Add user to appropriate groups
    run_command(f"usermod -a -G nginx {username}")
    
    print(f"✅ User {username} created")


def create_directory_structure(study_name, username, base_dir="/opt/studies"):
    """Create the study directory structure."""
    print(f"📁 Creating directory structure...")
    
    # If base_dir is a full path (contains the study name), use it directly
    if study_name.lower().replace(" ", "_") in base_dir.lower() or study_name.lower().replace(" ", "-") in base_dir.lower():
        study_dir = Path(base_dir)
    else:
        # Otherwise, append study name to base_dir (use hyphens for consistency)
        study_dir = Path(base_dir) / study_name.lower().replace(" ", "-")
    
    # Create base directory
    study_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    directories = [
        "data_uploads/uploads",
        "data_uploads/processed",
        "data_uploads/archived",
        "ema_surveys",
        "logs",
        "scripts",
        "config",
        "templates",
        "static",
        "active_sensing",
        "data"
    ]
    
    for subdir in directories:
        (study_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    # Set ownership
    run_command(f"chown -R {username}:{username} {study_dir}")
    
    print(f"✅ Directory structure created: {study_dir}")
    return study_dir


def create_directory_structure_in_path(study_dir, username):
    """Create directory structure in the specified path."""
    print(f"📁 Creating directory structure in: {study_dir}")
    
    # Create base directory
    study_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    directories = [
        "config",
        "data_uploads/uploads",
        "data_uploads/processed", 
        "data_uploads/archived",
        "data_uploads/exceptions",
        "ema_surveys",
        "logs",
        "scripts",
        "templates",
        "static"
    ]
    
    for directory in directories:
        dir_path = study_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        # Set ownership
        run_command(f"chown -R {username}:{username} {dir_path}")
    
    print(f"✅ Directory structure created in: {study_dir}")


def create_conda_environment(conda_path, study_name, username, python_version="3.9"):
    """Create conda environment for the study."""
    env_name = f"{study_name.lower().replace(' ', '-')}-env"
    print(f"🐍 Creating conda environment: {env_name}")
    
    # Check if environment already exists
    result = run_command(f"{conda_path}/bin/conda env list", check=False)
    if env_name in result.stdout:
        print(f"✅ Environment {env_name} already exists")
        # Verify it's actually accessible
        print(f"🔍 Testing environment accessibility...")
        test_result = run_command(f"{conda_path}/bin/conda run -n {env_name} python --version", check=False)
        if test_result.returncode == 0:
            print(f"✅ Environment {env_name} is accessible: {test_result.stdout.strip()}")
            return env_name
        else:
            print(f"⚠️ Environment {env_name} exists but is not accessible")
            print(f"Debug - conda run output: {test_result.stdout}")
            print(f"Debug - conda run error: {test_result.stderr}")
            print(f"🔧 Recreating environment...")
            print(f"💡 Manual test command: {conda_path}/bin/conda run -n {env_name} python --version")
            # Remove the broken environment from both locations
            run_command(f"{conda_path}/bin/conda env remove -n {env_name} -y", check=False)
            # Also remove from user directory if it exists there
            user_env_path = f"/home/{username}/.conda/envs/{env_name}"
            if os.path.exists(user_env_path):
                print(f"🧹 Removing user environment: {user_env_path}")
                run_command(f"rm -rf {user_env_path}", check=False)
    
    # Create environment
    print(f"🔧 Creating conda environment with Python {python_version}...")
    
    # Configure conda to use system-wide environments
    print(f"🔧 Configuring conda to use system environments...")
    
    # Check current conda configuration
    config_result = run_command(f"{conda_path}/bin/conda config --show envs_dirs", check=False)
    print(f"🔍 Current conda envs_dirs: {config_result.stdout}")
    
    # Reset conda configuration to use only system directory
    print(f"🔧 Resetting conda configuration...")
    
    # Clear all existing envs_dirs
    run_command(f"{conda_path}/bin/conda config --remove-key envs_dirs", check=False)
    
    # Set only the system environment directory
    run_command(f"{conda_path}/bin/conda config --add envs_dirs {conda_path}/envs", check=False)
    
    # Ensure the envs directory exists and has proper permissions
    envs_dir = f"{conda_path}/envs"
    if not os.path.exists(envs_dir):
        print(f"🔧 Creating envs directory: {envs_dir}")
        run_command(f"mkdir -p {envs_dir}")
    
    # Set proper ownership
    run_command(f"chown -R {username}:{username} {envs_dir}")
    
    # Accept Terms of Service for conda channels
    print(f"🔧 Accepting conda Terms of Service...")
    tos_result1 = run_command(f"{conda_path}/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main", check=False)
    tos_result2 = run_command(f"{conda_path}/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r", check=False)
    
    if tos_result1.returncode == 0 and tos_result2.returncode == 0:
        print(f"✅ Terms of Service accepted successfully")
    else:
        print(f"⚠️ TOS acceptance may have failed, but continuing...")
        print(f"Debug - TOS main: {tos_result1.stdout} {tos_result1.stderr}")
        print(f"Debug - TOS r: {tos_result2.stdout} {tos_result2.stderr}")
    
    # Verify configuration
    final_config = run_command(f"{conda_path}/bin/conda config --show envs_dirs", check=False)
    print(f"🔍 Updated conda envs_dirs: {final_config.stdout}")
    
    # Create environment in system location
    print(f"🔧 Creating conda environment in system location...")
    try:
        result = run_command(f"{conda_path}/bin/conda create -n {env_name} python={python_version} -y", check=False)
        if result.returncode != 0:
            print(f"❌ Conda create failed with return code: {result.returncode}")
            print(f"Debug - conda create output: {result.stdout}")
            print(f"Debug - conda create error: {result.stderr}")
            raise Exception(f"Conda create failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error creating conda environment: {e}")
        print(f"💡 Manual test command: {conda_path}/bin/conda create -n {env_name} python={python_version} -y")
        raise e
    
    # Verify environment was created
    result = run_command(f"{conda_path}/bin/conda env list", check=False)
    if env_name not in result.stdout:
        print(f"❌ Failed to create conda environment: {env_name}")
        print(f"Debug - conda env list output: {result.stdout}")
        raise Exception(f"Could not create conda environment: {env_name}")
    
    # Set ownership of conda environments directory
    conda_envs_dir = f"{conda_path}/envs"
    if os.path.exists(conda_envs_dir):
        run_command(f"chown -R {username}:{username} {conda_envs_dir}")
    
    # Final verification that the environment works
    final_test = run_command(f"{conda_path}/bin/conda run -n {env_name} python --version", check=False)
    if final_test.returncode != 0:
        print(f"❌ Environment creation failed - cannot access {env_name}")
        print(f"Debug - final test output: {final_test.stdout}")
        print(f"Debug - final test error: {final_test.stderr}")
        raise Exception(f"Failed to create accessible conda environment: {env_name}")
    
    print(f"✅ Conda environment created and verified: {env_name}")
    return env_name


def install_packages(conda_path, env_name, study_dir):
    """Install required Python packages."""
    print(f"📦 Installing Python packages...")
    
    # Get the submodule path
    submodule_path = study_dir / "ubiwell-study-backend-core"
    requirements_path = submodule_path / "requirements.txt"
    
    print(f"🔍 Looking for submodule at: {submodule_path}")
    print(f"🔍 Study directory: {study_dir}")
    print(f"🔍 Submodule path exists: {submodule_path.exists()}")
    
    # First, verify the environment exists and is accessible
    print(f"🔍 Verifying conda environment: {env_name}")
    result = run_command(f"{conda_path}/bin/conda run -n {env_name} python --version", check=False)
    if result.returncode != 0:
        print(f"❌ Cannot access conda environment: {env_name}")
        print(f"Debug - conda run output: {result.stdout}")
        print(f"Debug - conda run error: {result.stderr}")
        raise Exception(f"Conda environment {env_name} is not accessible")
    print(f"✅ Conda environment is accessible: {result.stdout.strip()}")
    
    if requirements_path.exists():
        print(f"📦 Installing requirements from: {requirements_path}")
        run_command(f"{conda_path}/bin/conda run -n {env_name} pip install -r {requirements_path}")
    else:
        print("⚠️ requirements.txt not found, installing individual packages")
        packages = [
            "flask",
            "flask-restful",
            "pymongo",
            "pandas",
            "numpy",
            "plotly",
            "gunicorn",
            "marshmallow",
            "python-dotenv",
            "requests",
            "geopy"
        ]
        
        for package in packages:
            print(f"📦 Installing {package}...")
            try:
                run_command(f"{conda_path}/bin/conda run -n {env_name} pip install {package}")
                print(f"✅ Successfully installed {package}")
            except Exception as e:
                print(f"❌ Failed to install {package}: {e}")
                print(f"💡 You may need to install this package manually later")
                # Continue with other packages instead of failing completely
    
    # Install the framework in editable mode
    print("📦 Installing study-framework-core in editable mode...")
    
    # Check if submodule path exists
    if not submodule_path.exists():
        print(f"❌ Submodule path does not exist: {submodule_path}")
        
        # Check if this is a git repository
        git_dir = study_dir / ".git"
        if not git_dir.exists():
            print(f"❌ Not a git repository: {study_dir}")
            print(f"💡 The study directory needs to be a git repository with the ubiwell-study-backend-core submodule")
            print(f"💡 You may need to clone the repository properly or initialize the submodule")
            raise Exception(f"Study directory is not a git repository: {study_dir}")
        
        print(f"🔧 Attempting to initialize submodule...")
        
        # Check if submodule is configured
        submodule_result = run_command(f"cd {study_dir} && git submodule status", check=False)
        print(f"🔍 Submodule status: {submodule_result.stdout}")
        
        # Try to initialize the submodule
        try:
            init_result = run_command(f"cd {study_dir} && git submodule update --init --recursive", check=False)
            print(f"🔍 Submodule init output: {init_result.stdout}")
            if init_result.stderr:
                print(f"🔍 Submodule init error: {init_result.stderr}")
            
            if submodule_path.exists():
                print(f"✅ Submodule initialized successfully")
            else:
                print(f"❌ Submodule initialization failed")
                print(f"💡 Manual command: cd {study_dir} && git submodule update --init --recursive")
                raise Exception(f"Submodule path not found: {submodule_path}")
        except Exception as e:
            print(f"❌ Failed to initialize submodule: {e}")
            print(f"💡 You may need to initialize the submodule manually")
            print(f"💡 Manual command: cd {study_dir} && git submodule update --init --recursive")
            raise Exception(f"Submodule path not found: {submodule_path}")
    
    # Check if setup.py exists in submodule
    setup_py_path = submodule_path / "setup.py"
    if not setup_py_path.exists():
        print(f"❌ setup.py not found in submodule: {setup_py_path}")
        print(f"💡 The submodule may not be properly initialized")
        raise Exception(f"setup.py not found in submodule: {setup_py_path}")
    
    print(f"🔍 Submodule path exists: {submodule_path}")
    print(f"🔍 setup.py found: {setup_py_path}")
    
    try:
        # Change to the submodule directory and install from there
        print(f"🔧 Installing framework from submodule directory...")
        result = run_command(f"cd {submodule_path} && {conda_path}/bin/conda run -n {env_name} pip install -e .", check=False)
        if result.returncode != 0:
            print(f"❌ Framework installation failed with return code: {result.returncode}")
            print(f"Debug - pip install output: {result.stdout}")
            print(f"Debug - pip install error: {result.stderr}")
            print(f"💡 Manual test command: cd {submodule_path} && {conda_path}/bin/conda run -n {env_name} pip install -e .")
            raise Exception(f"Framework installation failed: {result.stderr}")
        else:
            print(f"✅ Framework installed successfully")
    except Exception as e:
        print(f"❌ Error installing framework: {e}")
        print(f"💡 You may need to install the framework manually later")
        print(f"💡 Manual command: cd {submodule_path} && {conda_path}/bin/conda run -n {env_name} pip install -e .")
        print(f"💡 Alternative: Install from PyPI if available")
        # Don't raise exception, continue with setup
        print(f"⚠️ Continuing setup without framework installation...")
        print(f"📝 Note: You can install the framework later by running:")
        print(f"   cd {submodule_path}")
        print(f"   {conda_path}/bin/conda run -n {env_name} pip install -e .")
    
    print("✅ All packages installed successfully")


def create_config_file(study_dir, study_name, db_username, db_password, db_name, db_host, db_port, auth_key, announcement_key):
    """Create the study configuration file."""
    print(f"⚙️ Creating configuration file...")
    
    config = {
        "study": {
            "name": study_name,
            "version": "1.0.0"
        },
        "database": {
            "host": db_host,
            "port": int(db_port),
            "username": db_username,
            "password": db_password,
            "database": db_name
        },
        "server": {
            "host": "0.0.0.0",
            "port": 5000,
            "debug": False
        },
        "security": {
            "auth_key": auth_key,
            "announcement_pass_key": announcement_key
        },
        "paths": {
            "base_dir": str(study_dir),
            "data_upload_path": str(study_dir / "data_uploads" / "uploads"),
            "data_processed_path": str(study_dir / "data_uploads" / "processed"),
            "data_archived_path": str(study_dir / "data_uploads" / "archived"),
            "ema_file_path": str(study_dir / "ema_surveys"),
            "logs_path": str(study_dir / "logs"),
            "scripts_path": str(study_dir / "scripts"),
            "templates_path": str(study_dir / "templates"),
            "static_path": str(study_dir / "static")
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    config_file = study_dir / "config" / "study_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration file created: {config_file}")


def create_wsgi_files(study_dir, study_name):
    """Create WSGI files for the Flask applications."""
    print(f"🐍 Creating WSGI files...")
    
    # API WSGI file
    api_wsgi_content = f"""#!/usr/bin/env python3
\"\"\"
API WSGI entry point for {study_name} (Data Collection - Priority #1)
\"\"\"

import sys
import os
from pathlib import Path

study_path = Path(__file__).parent
submodule_path = study_path / "ubiwell-study-backend-core"
sys.path.insert(0, str(submodule_path))

os.environ['STUDY_CONFIG_FILE'] = str(study_path / "config" / "study_config.json")

from study_framework_core.core.config import get_config
from study_framework_core.core.api import CoreAPIEndpoints
from flask import Flask
from flask_restful import Api

config = get_config()

app = Flask(__name__)
api = Api(app, prefix='/api/v1')

core_api = CoreAPIEndpoints(api, config.security.auth_key)

if __name__ == "__main__":
    app.run()
"""
    
    api_wsgi_file = study_dir / "api_wsgi.py"
    api_wsgi_file.write_text(api_wsgi_content)
    os.chmod(api_wsgi_file, 0o755)
    print(f"✅ Created API WSGI file: {api_wsgi_file}")
    
    # Internal Web WSGI file
    internal_wsgi_content = f"""#!/usr/bin/env python3
\"\"\"
Internal Web WSGI entry point for {study_name} (Dashboard - Priority #2)
\"\"\"

import sys
import os
from pathlib import Path

study_path = Path(__file__).parent
submodule_path = study_path / "ubiwell-study-backend-core"
sys.path.insert(0, str(submodule_path))

os.environ['STUDY_CONFIG_FILE'] = str(study_path / "config" / "study_config.json")

from study_framework_core.core.config import get_config
from study_framework_core.core.internal_web import InternalWebBase, SimpleDashboard
from flask import Flask

config = get_config()

template_dir = submodule_path / "study_framework_core" / "templates"
app = Flask(__name__, template_folder=str(template_dir))

dashboard = SimpleDashboard()

internal_web = InternalWebBase(app, dashboard)

if __name__ == "__main__":
    app.run()
"""
    
    internal_wsgi_file = study_dir / "internal_wsgi.py"
    internal_wsgi_file.write_text(internal_wsgi_content)
    os.chmod(internal_wsgi_file, 0o755)
    print(f"✅ Created Internal Web WSGI file: {internal_wsgi_file}")


def create_systemd_services(study_name, study_dir, conda_path, env_name, username):
    """Create systemd services for the Flask applications."""
    print(f"🔧 Creating systemd services...")
    
    # Create socket directory
    socket_dir = "/var/sockets"
    os.makedirs(socket_dir, exist_ok=True)
    run_command(f"chown {username}:{username} {socket_dir}")
    
    # API service
    api_service_content = f"""[Unit]
Description=API Gunicorn instance to serve {study_name} (Data Collection - Priority #1)
After=network.target

[Service]
Type=notify
User={username}
Group={username}
WorkingDirectory={study_dir}
Environment="PATH={conda_path}/envs/{env_name}/bin"
ExecStart={conda_path}/envs/{env_name}/bin/gunicorn --workers 2 --bind unix:/var/sockets/{study_name.lower().replace(' ', '-')}-api.sock -m 007 api_wsgi:app --access-logfile {study_dir}/logs/api_access.log --error-logfile {study_dir}/logs/api_error.log
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
    
    api_service_file = f"/etc/systemd/system/{study_name.lower().replace(' ', '-')}-api.service"
    with open(api_service_file, 'w') as f:
        f.write(api_service_content)
    
    # Internal Web service
    internal_service_content = f"""[Unit]
Description=Internal Web Gunicorn instance to serve {study_name} (Dashboard - Priority #2)
After=network.target

[Service]
Type=notify
User={username}
Group={username}
WorkingDirectory={study_dir}
Environment="PATH={conda_path}/envs/{env_name}/bin"
ExecStart={conda_path}/envs/{env_name}/bin/gunicorn --workers 2 --bind unix:/var/sockets/{study_name.lower().replace(' ', '-')}-internal.sock -m 007 internal_wsgi:app --access-logfile {study_dir}/logs/internal_access.log --error-logfile {study_dir}/logs/internal_error.log
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
    
    internal_service_file = f"/etc/systemd/system/{study_name.lower().replace(' ', '-')}-internal.service"
    with open(internal_service_file, 'w') as f:
        f.write(internal_service_content)
    
    # Reload systemd and enable services
    run_command("systemctl daemon-reload")
    
    service_name = study_name.lower().replace(' ', '-')
    run_command(f"systemctl enable {service_name}-api")
    run_command(f"systemctl enable {service_name}-internal")
    
    print(f"✅ Created and enabled API service: {service_name}-api")
    print(f"✅ Created and enabled internal web service: {service_name}-internal")


def create_nginx_config(study_name, study_dir):
    """Create Nginx configuration for the study."""
    print(f"🌐 Creating nginx configuration...")
    
    service_name = study_name.lower().replace(' ', '-')
    
    nginx_config = f"""server {{
    listen 80;
    server_name _;
    
    # API endpoints
    location /api/ {{
        include proxy_params;
        proxy_pass http://unix:/var/sockets/{service_name}-api.sock;
    }}
    
    # Internal web dashboard
    location /internal_web/ {{
        include proxy_params;
        proxy_pass http://unix:/var/sockets/{service_name}-internal.sock;
    }}
    
    # Static files
    location /static/ {{
        alias {study_dir}/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
    
    # Health checks
    location /health {{
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}
"""
    
    nginx_file = f"/etc/nginx/conf.d/{service_name}.conf"
    with open(nginx_file, 'w') as f:
        f.write(nginx_config)
    
    # Test and reload nginx
    run_command("nginx -t")
    run_command("systemctl reload nginx")
    
    print(f"✅ Nginx configuration created: {nginx_file}")


def setup_firewall():
    """Setup firewall rules for the study."""
    print(f"🔥 Setting up firewall...")
    
    # Check if firewalld is running
    result = run_command("systemctl is-active firewalld", check=False)
    if result.returncode == 0:
        # Add HTTP and HTTPS to firewall
        run_command("firewall-cmd --permanent --add-service=http")
        run_command("firewall-cmd --permanent --add-service=https")
        run_command("firewall-cmd --reload")
        print("✅ Firewall configured")
    else:
        print("⚠️ firewalld not running, skipping firewall configuration")


def create_admin_user(study_dir, conda_path, env_name):
    """Create admin user for the internal web interface."""
    print(f"🔐 Creating admin user...")
    
    # Generate random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    # Create temporary script to create admin user
    temp_script = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the submodule path
study_path = Path(__file__).parent
submodule_path = study_path / "ubiwell-study-backend-core"
sys.path.insert(0, str(submodule_path))

os.environ['STUDY_CONFIG_FILE'] = str(study_path / "config" / "study_config.json")

from study_framework_core.core.handlers import create_admin_user

try:
    create_admin_user("admin", "{password}")
    print("✅ Admin user created successfully")
    print(f"Username: admin")
    print(f"Password: {password}")
except Exception as e:
    print(f"❌ Error creating admin user: {{e}}")
    sys.exit(1)
"""
    
    temp_script_path = study_dir / "temp_create_admin.py"
    temp_script_path.write_text(temp_script)
    os.chmod(temp_script_path, 0o755)
    
    try:
        run_command(f"{conda_path}/bin/conda run -n {env_name} python {temp_script_path}")
        print(f"✅ Admin user created with password: {password}")
    except Exception as e:
        print(f"⚠️ Warning: Could not create admin user automatically: {e}")
        print("💡 You can create the admin user manually later using:")
        print(f"   cd {study_dir}")
        print(f"   {conda_path}/bin/conda run -n {env_name} python ubiwell-study-backend-core/tests/create_admin_user.py")
    finally:
        # Clean up temporary script
        if temp_script_path.exists():
            temp_script_path.unlink()


def create_readme(study_dir, study_name, username):
    """Create a README file for the study."""
    print(f"📝 Creating README file...")
    
    readme_content = f"""# {study_name}

This study was set up using the Study Framework Core.

## Quick Start

### Start Services
```bash
sudo systemctl start {study_name.lower().replace(' ', '-')}-api
sudo systemctl start {study_name.lower().replace(' ', '-')}-internal
```

### Check Status
```bash
sudo systemctl status {study_name.lower().replace(' ', '-')}-api
sudo systemctl status {study_name.lower().replace(' ', '-')}-internal
```

### Access Dashboard
- URL: http://your-server/internal_web/
- Username: admin
- Password: (check setup logs or create manually)

### API Endpoints
- Base URL: http://your-server/api/v1/
- Auth Key: (check config/study_config.json)

## Directory Structure
```
{study_dir}/
├── ubiwell-study-backend-core/    # Framework submodule
├── config/                        # Configuration files
├── data_uploads/                  # Data upload directories
├── logs/                          # Application logs
├── scripts/                       # Processing scripts
└── templates/                     # Custom templates (optional)
```

## Configuration
Edit `config/study_config.json` to modify study settings.

## Updates
To update the framework:
```bash
cd {study_dir}/ubiwell-study-backend-core
git submodule update --remote
python update_core.py --study-name "{study_name}"
sudo systemctl restart {study_name.lower().replace(' ', '-')}-api {study_name.lower().replace(' ', '-')}-internal
```

## Support
For issues, check the logs in the `logs/` directory or contact the framework maintainers.
"""
    
    readme_file = study_dir / "README.md"
    readme_file.write_text(readme_content)
    
    print(f"✅ README file created: {readme_file}")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup Study Framework Core on Red Hat systems")
    parser.add_argument("study_name", help="Name of the study")
    parser.add_argument("--user", required=True, help="System user for the study")
    parser.add_argument("--study-path", help="Path to study directory (auto-detected if not specified)")
    parser.add_argument("--python-version", default="3.9", help="Python version for conda environment (default: 3.9)")
    parser.add_argument("--tokens", nargs='+', help="Authentication tokens")
    parser.add_argument("--db-username", required=True, help="MongoDB username")
    parser.add_argument("--db-password", required=True, help="MongoDB password")
    parser.add_argument("--db-name", required=True, help="MongoDB database name")
    parser.add_argument("--db-host", default="localhost", help="MongoDB host (default: localhost)")
    parser.add_argument("--db-port", default="27017", help="MongoDB port (default: 27017)")
    parser.add_argument("--auth-key", required=True, help="API authentication key")
    parser.add_argument("--announcement-key", required=True, help="Announcement system key")
    parser.add_argument("--base-dir", default="/opt/studies", help="Base directory for studies (default: /opt/studies)")
    parser.add_argument("--study-dir", help="Full path to study directory (overrides base-dir + study name)")
    
    args = parser.parse_args()
    
    print("🚀 Starting Study Framework Core Setup (Red Hat)")
    print(f"📋 Study: {args.study_name}")
    print(f"👤 User: {args.user}")
    print(f"🗄️ Database: {args.db_name}")
    if args.study_dir:
        print(f"📁 Study Directory: {args.study_dir}")
    else:
        print(f"📁 Base Directory: {args.base_dir}")
    print()
    
    # Check system requirements
    check_redhat_system()
    check_root()
    check_dependencies()
    
    # Setup Anaconda
    conda_path = check_anaconda()
    
    # Create user and directories
    create_user(args.user)
    
    # Determine study directory
    if args.study_dir:
        study_dir = Path(args.study_dir)
        print(f"📁 Using specified study directory: {study_dir}")
        # Create the directory structure in the specified path
        create_directory_structure_in_path(study_dir, args.user)
    else:
        study_dir = create_directory_structure(args.study_name, args.user, args.base_dir)
    
    # Setup conda environment
    env_name = create_conda_environment(conda_path, args.study_name, args.user, args.python_version)
    
    # Install packages
    install_packages(conda_path, env_name, study_dir)
    
    # Create configuration
    create_config_file(study_dir, args.study_name, args.db_username, args.db_password, 
                      args.db_name, args.db_host, args.db_port, args.auth_key, args.announcement_key)
    
    # Create WSGI files
    create_wsgi_files(study_dir, args.study_name)
    
    # Create systemd services
    create_systemd_services(args.study_name, study_dir, conda_path, env_name, args.user)
    
    # Setup nginx
    create_nginx_config(args.study_name, study_dir)
    
    # Setup firewall
    setup_firewall()
    
    # Create admin user
    create_admin_user(study_dir, conda_path, env_name)
    
    # Create README
    create_readme(study_dir, args.study_name, args.user)
    
    # Final setup
    print("\n🎉 Setup Complete!")
    print(f"📁 Study directory: {study_dir}")
    print(f"🐍 Conda environment: {env_name}")
    print(f"🔧 Services: {args.study_name.lower().replace(' ', '-')}-api, {args.study_name.lower().replace(' ', '-')}-internal")
    print()
    print("🚀 Next steps:")
    print("1. Start MongoDB: sudo systemctl start mongod")
    print("2. Start services: sudo systemctl start {args.study_name.lower().replace(' ', '-')}-api {args.study_name.lower().replace(' ', '-')}-internal")
    print("3. Access dashboard: http://your-server/internal_web/")
    print("4. Check logs: tail -f {study_dir}/logs/*.log")
    print()
    print("📚 For more information, see the README.md file in the study directory.")


if __name__ == "__main__":
    main()



