#!/usr/bin/env python3
"""
Comprehensive setup script for study framework deployment with submodule support.

This script handles:
1. Submodule validation and setup
2. Conda environment creation
3. Package installation
4. Systemd service creation
5. Nginx configuration
6. Directory structure setup
7. README generation with extension instructions
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from string import Template
from typing import Dict, Any
import json
from datetime import datetime


def run_command(command, check=True, capture_output=False):
    """Run a shell command and handle errors."""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=check)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        if check:
            sys.exit(1)
        return False


def check_submodule_setup():
    """Check if submodule is properly set up."""
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


def ensure_gitmodules():
    """Create .gitmodules file if it doesn't exist."""
    print("📝 Checking .gitmodules file...")
    
    gitmodules_path = Path("../.gitmodules")
    if not gitmodules_path.exists():
        print("📝 Creating .gitmodules file...")
        gitmodules_content = """[submodule "ubiwell-study-backend-core"]
    path = ubiwell-study-backend-core
    url = https://github.com/your-org/ubiwell-study-backend-core.git
    branch = main
"""
        gitmodules_path.write_text(gitmodules_content)
        print("✅ Created .gitmodules file")
    else:
        print("✅ .gitmodules file already exists")


def get_framework_version():
    """Get the current framework version."""
    try:
        # Try to get git commit hash
        commit_hash = run_command("git rev-parse --short HEAD", capture_output=True)
        return f"commit {commit_hash}"
    except:
        return "unknown"


def create_study_readme(study_name, study_dir):
    """Create a README.md with extension instructions."""
    print("📖 Creating README.md with extension instructions...")
    
    readme_content = f"""# {study_name}

This study uses the Ubiwell Study Framework.

## Setup
- Framework: ubiwell-study-backend-core (submodule)
- Created: {datetime.now().strftime('%Y-%m-%d')}
- Framework version: {get_framework_version()}

## Structure
- `ubiwell-study-backend-core/` - Framework code
- `config/` - Study configuration
- `data/` - Study data
- `logs/` - Application logs
- `scripts/` - Study-specific scripts

## Extending the Study

### Adding Custom Data Processing
1. Create custom scripts in `scripts/` directory
2. Import framework components:
   ```python
   from study_framework_core.core.handlers import get_db
   from study_framework_core.core.config import get_config
   ```

### Adding Custom API Endpoints
1. Extend the core API in your own module
2. Import base classes:
   ```python
   from study_framework_core.core.api import APIBase, CoreAPIEndpoints
   ```

### Adding Custom Dashboard Views
1. Create custom dashboard classes
2. Extend the base dashboard:
   ```python
   from study_framework_core.core.dashboard import DashboardBase
   ```

### Adding Custom Data Types
1. Add new collections to `config.py`
2. Create processing scripts for new data types
3. Update dashboard to display new data

### Configuration
- Study-specific config: `config/study_config.json`
- Framework config: `ubiwell-study-backend-core/study_framework_core/core/config.py`

## Updates
To update the framework:
```bash
cd ubiwell-study-backend-core
git submodule update --remote
python update_core.py
```

## Development
- Framework code: `ubiwell-study-backend-core/`
- Study-specific code: `scripts/`, `config/`
- Templates: `templates/` (extends framework templates)

## Services
- API Service: `{study_name.lower().replace(' ', '-')}-api`
- Internal Web Service: `{study_name.lower().replace(' ', '-')}-internal`

## Access URLs
- API: https://your-domain.com/{study_name.lower().replace(' ', '_')}/api/v1/
- Dashboard: https://your-domain.com/{study_name.lower().replace(' ', '_')}/internal_web
- API Health: https://your-domain.com/{study_name.lower().replace(' ', '_')}/api/health
- Internal Health: https://your-domain.com/{study_name.lower().replace(' ', '_')}/internal/health
"""
    
    readme_path = Path("../README.md")
    readme_path.write_text(readme_content)
    print("✅ Created README.md with extension instructions")


def check_anaconda():
    """Check if Anaconda/Miniconda is installed and find the best path."""
    print("🔍 Looking for Anaconda/Miniconda installations...")
    
    # Common Anaconda installation paths (since we're running as sudo)
    common_paths = [
        "/mnt/study/anaconda3/bin/conda",
        "/opt/anaconda3/bin/conda",
        "/usr/local/anaconda3/bin/conda",
        "/home/*/anaconda3/bin/conda",
        "/home/*/miniconda3/bin/conda",
        "/usr/share/anaconda3/bin/conda",
        "/usr/share/miniconda3/bin/conda",
    ]
    
    found_installations = []
    
    # Check each common path
    for path_pattern in common_paths:
        if '*' in path_pattern:
            # Handle glob patterns
            import glob
            matches = glob.glob(path_pattern)
            for match in matches:
                if os.path.exists(match):
                    found_installations.append(match)
        else:
            # Direct path
            if os.path.exists(path_pattern):
                found_installations.append(path_pattern)
    
    # If found multiple installations, let user choose
    if len(found_installations) > 1:
        print(f"✅ Found {len(found_installations)} Anaconda/Miniconda installations:")
        for i, path in enumerate(found_installations, 1):
            print(f"  {i}. {path}")
        
        while True:
            try:
                choice = input(f"\nSelect installation (1-{len(found_installations)}) or press Enter for first option: ").strip()
                if not choice:
                    selected_path = found_installations[0]
                    break
                else:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(found_installations):
                        selected_path = found_installations[choice_idx]
                        break
                    else:
                        print(f"❌ Invalid choice. Please enter 1-{len(found_installations)}")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
        
        print(f"✅ Using conda at: {selected_path}")
        return selected_path
    
    # If found exactly one installation
    elif len(found_installations) == 1:
        selected_path = found_installations[0]
        print(f"✅ Found conda at: {selected_path}")
        return selected_path
    
    # If no installations found
    else:
        print("❌ No Anaconda/Miniconda installations found in common locations.")
        print("Common locations checked:")
        for path in common_paths:
            print(f"  - {path}")
        
        print("\n💡 Options:")
        print("1. Install Anaconda/Miniconda automatically")
        print("2. Provide the path to your conda installation")
        print("3. Exit and install manually")
        
        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                return install_anaconda()
            elif choice == "2":
                user_path = input("Enter the full path to conda: ").strip()
                if os.path.exists(user_path):
                    print(f"✅ Using conda at: {user_path}")
                    return user_path
                else:
                    print(f"❌ Path does not exist: {user_path}")
                    continue
            elif choice == "3":
                print("❌ Setup cancelled. Please install Anaconda/Miniconda manually.")
                print("Download from: https://docs.conda.io/en/latest/miniconda.html")
                sys.exit(1)
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")


def install_anaconda():
    """Install Anaconda/Miniconda automatically."""
    print("🚀 Installing Anaconda/Miniconda...")
    
    # Ask user for installation path
    while True:
        install_path = input("Enter installation path (default: /mnt/study/anaconda3): ").strip()
        if not install_path:
            install_path = "/mnt/study/anaconda3"
        
        if os.path.exists(install_path):
            overwrite = input(f"Path {install_path} already exists. Overwrite? (y/N): ").strip().lower()
            if overwrite in ['y', 'yes']:
                break
            else:
                continue
        else:
            break
    
    print(f"📦 Installing Anaconda to: {install_path}")
    
    # Download and install Miniconda
    try:
        # Create installation directory
        os.makedirs(os.path.dirname(install_path), exist_ok=True)
        
        # Download Miniconda installer
        import urllib.request
        import tempfile
        
        miniconda_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        installer_path = "/tmp/miniconda_installer.sh"
        
        print("📥 Downloading Miniconda installer...")
        urllib.request.urlretrieve(miniconda_url, installer_path)
        
        # Make installer executable
        os.chmod(installer_path, 0o755)
        
        # Run installer
        print("🔧 Running Miniconda installer...")
        install_command = f"bash {installer_path} -b -p {install_path} -f"
        run_command(install_command)
        
        # Clean up installer
        os.remove(installer_path)
        
        conda_path = f"{install_path}/bin/conda"
        if os.path.exists(conda_path):
            print(f"✅ Anaconda installed successfully at: {conda_path}")
            return conda_path
        else:
            print("❌ Installation failed. Conda not found at expected location.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        print("💡 Please install Anaconda/Miniconda manually from: https://docs.conda.io/en/latest/miniconda.html")
        sys.exit(1)


def create_conda_environment(study_name, python_version="3.9", conda_path=None):
    """Create a conda environment for the study."""
    env_name = f"{study_name.lower().replace(' ', '-')}-env"
    
    print(f"🔧 Creating conda environment: {env_name}")
    
    # Check if environment already exists
    env_exists = run_command(f"{conda_path} env list | grep {env_name}", check=False, capture_output=True)
    
    if env_exists:
        print(f"⚠️  Environment {env_name} already exists. Removing it...")
        run_command(f"{conda_path} env remove -n {env_name} -y")
    
    # Create new environment
    run_command(f"{conda_path} create -n {env_name} python={python_version} -y")
    
    print(f"✅ Created conda environment: {env_name}")
    return env_name


def install_packages(env_name, study_path, conda_path=None):
    """Install required packages in the conda environment."""
    print(f"📦 Installing packages in {env_name}")
    
    # Get the requirements.txt path
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    if requirements_path.exists():
        print(f"  Installing from requirements.txt: {requirements_path}")
        run_command(f"{conda_path} run -n {env_name} pip install -r {requirements_path}")
    else:
        print("⚠️  requirements.txt not found, installing packages individually...")
        # Fallback to individual packages
        conda_packages = [
            "flask",
            "flask-restful", 
            "pymongo",
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "python-dotenv",
            "requests",
            "marshmallow",
            "werkzeug",
            "geopy",
            "plotly"
        ]
        
        for package in conda_packages:
            print(f"  Installing {package}...")
            run_command(f"{conda_path} run -n {env_name} pip install {package}")
    
    # Install the study framework core in editable mode for easy updates
    print("  Installing study-framework-core in editable mode...")
    run_command(f"{conda_path} run -n {env_name} pip install -e .")
    
    # Install gunicorn if not already installed
    print("  Installing gunicorn...")
    run_command(f"{conda_path} run -n {env_name} pip install gunicorn")
    
    print("✅ All packages installed successfully")


def create_directory_structure(study_name, base_dir, user):
    """Create the directory structure for the study."""
    # Use the base_dir directly as the study directory (no nested folder)
    study_dir = Path(base_dir)
    
    directories = [
        study_dir,
        study_dir / "logs",
        study_dir / "data",
        study_dir / "static",
        study_dir / "uploads",
        study_dir / "config",
        study_dir / "templates",
        study_dir / "scripts",
        study_dir / "static" / "css",
        study_dir / "static" / "js",
        study_dir / "data_uploads" / "uploads",
        study_dir / "data_uploads" / "processed",
        study_dir / "data_uploads" / "exceptions",
        study_dir / "data_uploads" / "logs",
        study_dir / "active_sensing",
        study_dir / "ema_surveys",
        study_dir / "config-files" / "global",
    ]
    
    print(f"📁 Creating directory structure in {study_dir}")
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        # Set ownership to the user
        run_command(f"chown {user}:{user} {directory}")
        print(f"  Created: {directory}")
    
    # Copy processing scripts
    copy_processing_scripts(study_dir)
    
    return study_dir


def create_systemd_service(study_name, env_name, study_dir, user, base_dir, conda_path=None):
    """Create separate systemd services for API and internal web."""
    api_service_name = f"{study_name.lower().replace(' ', '-')}-api"
    internal_service_name = f"{study_name.lower().replace(' ', '-')}-internal"
    
    # Create socket directory
    socket_dir = "/var/sockets"
    run_command(f"mkdir -p {socket_dir}")
    run_command(f"chown {user}:www-data {socket_dir}")
    run_command(f"chmod 755 {socket_dir}")
    
    # Get conda environment path
    conda_prefix = run_command(f"{conda_path} run -n {env_name} python -c 'import sys; print(sys.prefix)'", capture_output=True)
    
    # API Service (Priority #1 - Data Collection)
    api_service_content = f"""[Unit]
Description=API Gunicorn instance to serve {study_name} (Data Collection - Priority #1)
After=network.target

[Service]
User={user}
Group=www-data
WorkingDirectory={study_dir}
Environment="PATH={conda_prefix}/bin"
ExecStart={conda_prefix}/bin/gunicorn --workers 3 --bind unix:/var/sockets/{api_service_name}.sock -m 007 api_wsgi:app --access-logfile {study_dir}/logs/api_gunicorn_access.log --error-logfile {study_dir}/logs/api_gunicorn_error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    
    api_service_file = f"/etc/systemd/system/{api_service_name}.service"
    
    print(f"🔧 Creating API systemd service: {api_service_file}")
    
    with open(api_service_file, 'w') as f:
        f.write(api_service_content)
    
    # Internal Web Service (Priority #2 - Dashboard)
    internal_service_content = f"""[Unit]
Description=Internal Web Gunicorn instance to serve {study_name} (Dashboard - Priority #2)
After=network.target

[Service]
User={user}
Group=www-data
WorkingDirectory={study_dir}
Environment="PATH={conda_prefix}/bin"
ExecStart={conda_prefix}/bin/gunicorn --workers 2 --bind unix:/var/sockets/{internal_service_name}.sock -m 007 internal_wsgi:app --access-logfile {study_dir}/logs/internal_gunicorn_access.log --error-logfile {study_dir}/logs/internal_gunicorn_error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    
    internal_service_file = f"/etc/systemd/system/{internal_service_name}.service"
    
    print(f"🔧 Creating internal web systemd service: {internal_service_file}")
    
    with open(internal_service_file, 'w') as f:
        f.write(internal_service_content)
    
    # Reload systemd and enable services
    run_command("systemctl daemon-reload")
    run_command(f"systemctl enable {api_service_name}")
    run_command(f"systemctl enable {internal_service_name}")
    
    print(f"✅ Created and enabled API service: {api_service_name}")
    print(f"✅ Created and enabled internal web service: {internal_service_name}")
    return api_service_name, internal_service_name


def create_nginx_config(study_name, api_service_name, internal_service_name, test_config=True):
    """Create nginx configuration with separate services."""
    nginx_config = f"""# {study_name} Nginx Configuration (Separate Services)

server {{
    listen 80;
    server_name _;

    # API endpoints (Priority #1 - Data Collection)
    location /api/v1/ {{
        include proxy_params;
        proxy_pass http://unix:/var/sockets/{api_service_name}.sock;
    }}

    # Internal web dashboard (Priority #2 - Dashboard)
    location /internal_web {{
        # Allow specific IP ranges (customize as needed)
        allow 129.10.0.0/16;
        allow 129.10.128.0/17;
        allow 129.10.64.0/18;
        allow 155.33.0.0/16;
        allow 155.33.0.0/17;
        allow 10.0.0.0/8;
        deny all;

        include proxy_params;
        proxy_pass http://unix:/var/sockets/{internal_service_name}.sock;
    }}

    # Health check endpoints
    location /api/health {{
        include proxy_params;
        proxy_pass http://unix:/var/sockets/{api_service_name}.sock;
    }}

    location /internal/health {{
        include proxy_params;
        proxy_pass http://unix:/var/sockets/{internal_service_name}.sock;
    }}

    # Static files
    location /static/ {{
        alias /mnt/study/{study_name.lower().replace(' ', '-')}/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
    
    nginx_file = f"/etc/nginx/sites-available/{study_name.lower().replace(' ', '-')}"
    
    print(f"🌐 Creating nginx configuration: {nginx_file}")
    
    with open(nginx_file, 'w') as f:
        f.write(nginx_config)
    
    # Create symlink to enable the site
    nginx_enabled = f"/etc/nginx/sites-enabled/{study_name.lower().replace(' ', '-')}"
    if os.path.exists(nginx_enabled):
        os.remove(nginx_enabled)
    
    os.symlink(nginx_file, nginx_enabled)
    
    # Test nginx configuration (only if requested)
    if test_config:
        if run_command("nginx -t", check=False):
            print("✅ Nginx configuration is valid")
            run_command("systemctl reload nginx")
        else:
            print("❌ Nginx configuration is invalid. Please check the configuration.")
    else:
        print("⚠️  Nginx configuration created but not tested (will test after services are ready)")
    
    return nginx_file


def create_wsgi_files(study_dir, study_name):
    """Create separate WSGI files for API and internal web."""
    
    # API WSGI file (Priority #1 - Data Collection)
    api_wsgi_content = f"""#!/usr/bin/env python3
\"\"\"
API WSGI entry point for {study_name} (Data Collection - Priority #1)
\"\"\"

import sys
import os
from pathlib import Path

# Add the submodule to Python path
study_path = Path(__file__).parent
submodule_path = study_path / "ubiwell-study-backend-core"
sys.path.insert(0, str(submodule_path))

# Set environment variable for config
os.environ['STUDY_CONFIG_FILE'] = str(study_path / "config" / "study_config.json")

from study_framework_core.core.config import get_config
from study_framework_core.core.api import CoreAPIEndpoints
from flask import Flask
from flask_restful import Api

# Load configuration
config = get_config()

# Create Flask app
app = Flask(__name__)

# Create Flask-RESTful API
api = Api(app, prefix='/api/v1')

# Create API instance
core_api = CoreAPIEndpoints(api, config.security.auth_key)

if __name__ == "__main__":
    app.run()
"""
    
    api_wsgi_file = study_dir / "api_wsgi.py"
    
    print(f"🐍 Creating API WSGI file: {api_wsgi_file}")
    
    with open(api_wsgi_file, 'w') as f:
        f.write(api_wsgi_content)
    
    # Internal Web WSGI file (Priority #2 - Dashboard)
    internal_wsgi_content = f"""#!/usr/bin/env python3
\"\"\"
Internal Web WSGI entry point for {study_name} (Dashboard - Priority #2)
\"\"\"

import sys
import os
from pathlib import Path

# Add the submodule to Python path
study_path = Path(__file__).parent
submodule_path = study_path / "ubiwell-study-backend-core"
sys.path.insert(0, str(submodule_path))

# Set environment variable for config
os.environ['STUDY_CONFIG_FILE'] = str(study_path / "config" / "study_config.json")

from study_framework_core.core.config import get_config
from study_framework_core.core.internal_web import InternalWebBase, SimpleDashboard
from flask import Flask

# Load configuration
config = get_config()

# Create Flask app
app = Flask(__name__)

# Create dashboard instance
dashboard = SimpleDashboard()

# Create internal web instance
internal_web = InternalWebBase(app, dashboard)

# Get the Flask app
app = internal_web.app

if __name__ == "__main__":
    app.run()
"""
    
    internal_wsgi_file = study_dir / "internal_wsgi.py"
    
    print(f"🐍 Creating internal web WSGI file: {internal_wsgi_file}")
    
    with open(internal_wsgi_file, 'w') as f:
        f.write(internal_wsgi_content)
    
    # Make both executable
    run_command(f"chmod +x {api_wsgi_file}")
    run_command(f"chmod +x {internal_wsgi_file}")
    
    return api_wsgi_file, internal_wsgi_file


def create_sample_config_files(study_dir: Path):
    """Create sample configuration files for the study."""
    # Create global config file
    global_config = {
        "study_name": "Sample Study",
        "version": "1.0.0",
        "features": {
            "ema_enabled": True,
            "daily_diary_enabled": True,
            "active_sensing_enabled": True
        },
        "data_collection": {
            "upload_interval": 3600,
            "max_file_size": 10485760
        }
    }
    
    global_config_path = study_dir / "config-files" / "global" / "config.json"
    with open(global_config_path, 'w') as f:
        json.dump(global_config, f, indent=2)
    
    # Create sample EMA file
    ema_config = {
        "ema_surveys": [
            {
                "id": "morning_survey",
                "title": "Morning Check-in",
                "questions": [
                    {
                        "id": "mood",
                        "type": "slider",
                        "question": "How are you feeling this morning?",
                        "min": 1,
                        "max": 10
                    }
                ]
            }
        ]
    }
    
    ema_file_path = study_dir / "ema_surveys" / "global" / "ema.json"
    ema_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ema_file_path, 'w') as f:
        json.dump(ema_config, f, indent=2)
    
    print(f"✅ Created sample config files in {study_dir}")


def create_admin_user(study_dir: Path, db_username: str, db_password: str, db_host: str, db_port: str, db_name: str, env_name: str = None, conda_path: str = None):
    """Create admin user for internal web access."""
    try:
        # Set up environment for database connection
        os.environ['STUDY_CONFIG_FILE'] = str(study_dir / "config" / "study_config.json")
        
        # Import after environment setup
        import sys
        sys.path.insert(0, str(study_dir))
        
        # Use conda environment if available
        if env_name and conda_path:
            # Create a temporary script to run in conda environment
            temp_script = study_dir / "temp_create_admin.py"
            temp_script_content = f'''#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the submodule to Python path
study_path = Path("{study_dir}")
submodule_path = study_path / "ubiwell-study-backend-core"
sys.path.insert(0, str(submodule_path))

os.environ['STUDY_CONFIG_FILE'] = "{study_dir}/config/study_config.json"

try:
    from study_framework_core.core.handlers import create_admin_user
    
    result = create_admin_user()
    print(f"SUCCESS:{{result['success']}}")
    print(f"USERNAME:{{result['username']}}")
    print(f"PASSWORD:{{result['password']}}")
    if not result['success']:
        print(f"ERROR:{{result['error']}}")
except Exception as e:
    print(f"SUCCESS:False")
    print(f"USERNAME:admin")
    print(f"PASSWORD:None")
    print(f"ERROR:{{str(e)}}")
'''
            temp_script.write_text(temp_script_content)
            
            # Run the script in conda environment
            cmd = f"{conda_path} run -n {env_name} python {temp_script}"
            result_output = run_command(cmd, capture_output=True)
            
            # Parse the output
            lines = result_output.split('\n')
            success = False
            username = "admin"
            password = None
            error = None
            
            for line in lines:
                if line.startswith("SUCCESS:"):
                    success = line.split(":", 1)[1].strip() == "True"
                elif line.startswith("USERNAME:"):
                    username = line.split(":", 1)[1].strip()
                elif line.startswith("PASSWORD:"):
                    password = line.split(":", 1)[1].strip()
                elif line.startswith("ERROR:"):
                    error = line.split(":", 1)[1].strip()
            
            # Clean up temp script
            temp_script.unlink()
            
            result = {"success": success, "username": username, "password": password, "error": error}
        else:
            # Fallback to direct import (may fail if dependencies not available)
            from study_framework_core.core.handlers import create_admin_user
            result = create_admin_user()
        
        if result['success']:
            print(f"✅ Admin user created successfully!")
            print(f"   Username: {result['username']}")
            print(f"   Password: {result['password']}")
            print(f"   ⚠️  Please save this password securely!")
            return result['password']
        else:
            print(f"❌ Failed to create admin user: {result['error']}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return None


def copy_processing_scripts(study_dir: Path):
    """Copy processing scripts to the study directory."""
    try:
        # Get the path to the core framework scripts
        core_scripts_dir = Path(__file__).parent / "study_framework_core" / "scripts"
        study_scripts_dir = study_dir / "scripts"
        
        if core_scripts_dir.exists():
            # Copy all shell scripts
            for script_file in core_scripts_dir.glob("*.sh"):
                dest_file = study_scripts_dir / script_file.name
                shutil.copy2(script_file, dest_file)
                dest_file.chmod(0o755)  # Make executable
                print(f"✅ Copied script: {script_file.name}")
        else:
            print(f"⚠️  Warning: Core scripts directory not found: {core_scripts_dir}")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not copy processing scripts: {e}")


def make_scripts_executable(study_dir: Path):
    """Make processing scripts executable."""
    try:
        scripts_dir = study_dir / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.sh"):
                script_file.chmod(0o755)
                print(f"✅ Made executable: {script_file.name}")
    except Exception as e:
        print(f"⚠️  Warning: Could not make scripts executable: {e}")


def create_study_config(study_name: str, study_dir: Path, db_username: str, db_password: str, 
                       db_host: str, db_port: str, db_name: str, auth_key: str, announcement_key: str) -> Dict[str, Any]:
    """Create study configuration file."""
    config_content = {
        "study_name": study_name,
        "database": {
            "host": db_host,
            "port": int(db_port),
            "username": db_username,
            "password": db_password,
            "database": db_name or f"{study_name.lower().replace(' ', '_')}_db"
        },
        "server": {
            "host": "127.0.0.1",  # Localhost for production with reverse proxy
            "port": 8000,  # Only used for development or direct access
            "workers": 3,
            "debug": False,
            "socket_path": f"/var/sockets/{study_name.lower().replace(' ', '-')}-study.sock"
        },
        "security": {
            "auth_key": auth_key,
            "tokens": ['your-auth-token'], # Placeholder, will be updated by user
            "announcement_pass_key": announcement_key
        },
        "paths": {
            "base_dir": str(study_dir),
            "logs_dir": f"{study_dir}/logs",
            "data_dir": f"{study_dir}/data",
            "static_dir": f"{study_dir}/static",
            "uploads_dir": f"{study_dir}/uploads",
            "data_upload_path": f"{study_dir}/data_uploads/uploads",
            "data_processed_path": f"{study_dir}/data_uploads/processed",
            "data_exceptions_path": f"{study_dir}/data_uploads/exceptions",
            "data_upload_logs_path": f"{study_dir}/data_uploads/logs",
            "active_sensing_upload_path": f"{study_dir}/active_sensing",
            "ema_file_path": f"{study_dir}/ema_surveys"
        },
        "logging": {
            "level": "INFO",
            "file_path": f"{study_dir}/logs/study.log"
        }
    }
    
    config_file = study_dir / "config" / "study_config.json"
    
    print(f"⚙️  Creating study configuration: {config_file}")
    
    with open(config_file, 'w') as f:
        json.dump(config_content, f, indent=2)
    
    return config_content


def create_requirements_file(study_dir):
    """Create requirements.txt file."""
    requirements_content = """# Study Framework Core
git+https://github.com/your-org/study-framework-core.git

# Flask and extensions
flask>=2.0.0
flask-restful>=0.3.9

# Database
pymongo>=4.0.0

# Data processing
pandas>=1.3.0
numpy>=1.21.0

# Visualization
matplotlib>=3.5.0
seaborn>=0.11.0

# Server
gunicorn>=20.1.0

# Utilities
python-dotenv>=0.19.0
requests>=2.25.0
"""
    
    requirements_file = study_dir / "requirements.txt"
    
    print(f"📋 Creating requirements file: {requirements_file}")
    
    with open(requirements_file, 'w') as f:
        f.write(requirements_content)
    
    return requirements_file


def create_readme(study_dir, study_name, service_name):
    """Create README file for the study."""
    readme_content = f"""# {study_name}

This study is deployed using the Study Framework Core.

## Quick Start

1. **Start the service:**
   ```bash
   sudo systemctl start {service_name}
   ```

2. **Check status:**
   ```bash
   sudo systemctl status {service_name}
   ```

3. **View logs:**
   ```bash
   sudo journalctl -u {service_name} -f
   ```

## Configuration

- **Config file:** `config/study_config.json`
- **Logs:** `logs/`
- **Data:** `data/`
- **Static files:** `static/`

## URLs

- **API:** `https://your-domain.com/{study_name.lower().replace(' ', '_')}/api/v1/`
- **Dashboard:** `https://your-domain.com/{study_name.lower().replace(' ', '_')}/internal_web`

## Maintenance

### Update the study:
```bash
cd {study_dir}
git pull
sudo systemctl restart {service_name}
```

### Update the framework:
```bash
conda activate {study_name.lower().replace(' ', '-')}-env
pip install --upgrade study-framework-core
sudo systemctl restart {service_name}
```

## Troubleshooting

1. **Check service status:**
   ```bash
   sudo systemctl status {service_name}
   ```

2. **Check nginx status:**
   ```bash
   sudo systemctl status nginx
   ```

3. **Check logs:**
   ```bash
   sudo tail -f {study_dir}/logs/gunicorn_error.log
   ```
"""
    
    readme_file = study_dir / "README.md"
    
    print(f"📚 Creating README file: {readme_file}")
    
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    return readme_file


def update_core_framework(study_name):
    """Update the core framework to the latest version."""
    env_name = f"{study_name.lower().replace(' ', '-')}-env"
    
    print(f"🔄 Updating core framework in {env_name}")
    
    # Check Anaconda installation
    conda_path = check_anaconda()
    
    # Update the core package
    run_command(f"{conda_path} run -n {env_name} pip install --upgrade -e .")
    
    print("✅ Core framework updated successfully!")
    print("💡 You may need to restart the services:")
    print(f"   sudo systemctl restart {study_name.lower().replace(' ', '-')}-api")
    print(f"   sudo systemctl restart {study_name.lower().replace(' ', '-')}-internal")


def main():
    parser = argparse.ArgumentParser(description='Setup a new study with conda, systemd, and nginx')
    parser.add_argument('study_name', help='Name of the study')
    parser.add_argument('--user', default='connect', help='System user to run the service')
    parser.add_argument('--study-path', help='Path to study directory (auto-detected if not specified)')
    parser.add_argument('--python-version', default='3.9', help='Python version for conda environment')
    parser.add_argument('--tokens', nargs='+', help='Authentication tokens')
    parser.add_argument('--db-username', help='MongoDB username')
    parser.add_argument('--db-password', help='MongoDB password')
    parser.add_argument('--db-host', default='localhost', help='MongoDB host')
    parser.add_argument('--db-port', default='27017', help='MongoDB port')
    parser.add_argument('--db-name', help='MongoDB database name (default: {study_name}_db)')
    parser.add_argument('--auth-key', help='Authentication key for API')
    parser.add_argument('--announcement-key', help='Announcement pass key')
    parser.add_argument('--update', action='store_true', help='Update core framework to latest version')
    
    args = parser.parse_args()
    
    # Handle update mode
    if args.update:
        update_core_framework(args.study_name)
        return
    
    # Auto-detect study path if not specified
    if not args.study_path:
        args.study_path = str(Path.cwd().parent)
        print(f"🔍 Auto-detected study directory: {args.study_path}")
    
    print(f"🚀 Setting up study: {args.study_name}")
    print(f"👤 User: {args.user}")
    print(f"📁 Study directory: {args.study_path}")
    
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script must be run as root (use sudo)")
        sys.exit(1)
    
    # Check Anaconda installation
    conda_path = check_anaconda()
    
    # Check submodule setup
    if not check_submodule_setup():
        sys.exit(1)
    ensure_gitmodules()

    # Create conda environment
    env_name = create_conda_environment(args.study_name, args.python_version, conda_path)
    
    # Create directory structure
    study_dir = create_directory_structure(args.study_name, args.study_path, args.user)
    
    # Install packages
    install_packages(env_name, Path.cwd(), conda_path)
    
    # Create WSGI files first
    api_wsgi_file, internal_wsgi_file = create_wsgi_files(study_dir, args.study_name)
    
    # Create systemd services
    api_service_name, internal_service_name = create_systemd_service(args.study_name, env_name, study_dir, args.user, args.study_path, conda_path)
    
    # Create nginx configuration (but don't test/reload yet)
    nginx_file = create_nginx_config(args.study_name, api_service_name, internal_service_name, test_config=False)
    
    # Create sample config files
    create_sample_config_files(study_dir)
    
    # Make processing scripts executable
    make_scripts_executable(study_dir)

    # Create configuration files
    config_file = create_study_config(
        args.study_name, 
        study_dir, 
        args.db_username or 'study_user',
        args.db_password or 'study_password',
        args.db_host or 'localhost',
        args.db_port or '27017',
        args.db_name,
        args.auth_key or 'your-auth-key',
        args.announcement_key or 'study123'
    )
    
    # Create admin user for internal web access (optional)
    print("🔐 Creating admin user for internal web access...")
    admin_password = create_admin_user(
        study_dir,
        args.db_username or 'study_user',
        args.db_password or 'study_password',
        args.db_host or 'localhost',
        args.db_port or '27017',
        args.db_name,
        env_name,
        conda_path
    )
    
    if admin_password:
        print("✅ Admin user created successfully")
    else:
        print("⚠️  Admin user creation failed - you can create it manually later")
        print("   Run: cd /mnt/study/bean-study && python create_admin_user.py")
    requirements_file = create_requirements_file(study_dir)
    
    # Create README with extension instructions
    create_study_readme(args.study_name, study_dir)
    
    # Set proper ownership
    run_command(f"chown -R {args.user}:{args.user} {study_dir}")
    
    # Test and reload nginx now that everything is set up
    print("🌐 Testing and reloading nginx configuration...")
    if run_command("nginx -t", check=False):
        print("✅ Nginx configuration is valid")
        run_command("systemctl reload nginx")
        print("✅ Nginx reloaded successfully")
    else:
        print("❌ Nginx configuration is invalid. Please check the configuration.")
    
    print(f"\n✅ Study setup completed successfully with separate services!")
    print(f"📁 Study directory: {study_dir}")
    print(f"🔧 API service name: {api_service_name} (Priority #1 - Data Collection)")
    print(f"🔧 Internal web service name: {internal_service_name} (Priority #2 - Dashboard)")
    print(f"🌐 Nginx config: {nginx_file}")
    print(f"🐍 Conda environment: {env_name}")
    
    print(f"\n📋 Next steps:")
    print(f"1. Edit {config_file} with your specific settings")
    print(f"2. Start the API service: sudo systemctl start {api_service_name}")
    print(f"3. Start the internal web service: sudo systemctl start {internal_service_name}")
    print(f"4. Check status: sudo systemctl status {api_service_name} {internal_service_name}")
    print(f"5. View logs: sudo journalctl -u {api_service_name} -f")
    print(f"6. View internal logs: sudo journalctl -u {internal_service_name} -f")
    print(f"7. Set up cron jobs: {study_dir}/scripts/setup_cron_jobs.sh --user {args.user} --env {env_name}")
    
    print(f"\n🌐 Access URLs:")
    print(f"  API: https://your-domain.com/{args.study_name.lower().replace(' ', '_')}/api/v1/")
    print(f"  Dashboard: https://your-domain.com/{args.study_name.lower().replace(' ', '_')}/internal_web")
    print(f"  API Health: https://your-domain.com/{args.study_name.lower().replace(' ', '_')}/api/health")
    print(f"  Internal Health: https://your-domain.com/{args.study_name.lower().replace(' ', '_')}/internal/health")
    
    if admin_password:
        print(f"\n🔐 Internal Web Login:")
        print(f"  Username: admin")
        print(f"  Password: {admin_password}")
        print(f"  ⚠️  Save this password securely!")
    
    print(f"\n🛡️  Reliability Benefits:")
    print(f"  • API service isolated from dashboard bugs")
    print(f"  • Data collection continues even if dashboard fails")
    print(f"  • Independent scaling and monitoring")
    print(f"  • Separate log files for easier debugging")
    
    print(f"\n📊 Data Processing:")
    print(f"  • Processing scripts available in: {study_dir}/scripts/")
    print(f"  • Manual processing: {study_dir}/scripts/process_data.sh --action process_data")
    print(f"  • Generate summaries: {study_dir}/scripts/generate_summaries.sh")
    print(f"  • Process Garmin files: {study_dir}/scripts/process_data.sh --action process_garmin")


if __name__ == "__main__":
    main()
