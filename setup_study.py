#!/usr/bin/env python3
"""
Comprehensive setup script for study framework deployment.

This script handles:
1. Conda environment creation
2. Package installation
3. Systemd service creation
4. Nginx configuration
5. Directory structure setup
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


def fix_conda_tos(base_dir="/mnt/study"):
    """Fix conda Terms of Service issues."""
    print("🔧 Fixing conda Terms of Service...")
    try:
        conda_path = f"{base_dir}/anaconda3/bin/conda"
        run_command(f"{conda_path} tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main", check=False)
        run_command(f"{conda_path} tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r", check=False)
        print("✅ Conda Terms of Service fixed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to fix conda ToS: {e}")
        return False

def check_anaconda(base_dir="/mnt/study"):
    """Check if Anaconda/Miniconda is installed, install if not found."""
    # Check if Anaconda is installed at the expected location
    anaconda_dir = Path(base_dir) / "anaconda3"
    conda_path = f"{base_dir}/anaconda3/bin/conda"
    
    if not anaconda_dir.exists() or not Path(conda_path).exists():
        print("❌ Anaconda/Miniconda not found.")
        print("🔧 Installing Anaconda automatically...")
        
        # Create base directory if it doesn't exist
        run_command(f"mkdir -p {base_dir}")
        
        # Download and install Anaconda
        anaconda_url = "https://repo.anaconda.com/archive/Anaconda3-2025.06-0-Linux-x86_64.sh"
        installer_path = "/tmp/anaconda_installer.sh"
        
        print("📥 Downloading Anaconda...")
        run_command(f"wget {anaconda_url} -O {installer_path}")
        
        print(f"🔧 Installing Anaconda to {base_dir}/anaconda3...")
        run_command(f"bash {installer_path} -b -p {base_dir}/anaconda3")
        
        # Add to PATH for current session
        os.environ['PATH'] = f"{base_dir}/anaconda3/bin:{os.environ['PATH']}"
        
        # Add to system-wide profile for all users
        profile_path = "/etc/profile.d/conda.sh"
        conda_init = f"""#!/bin/bash
# Added by study framework setup
export PATH="{base_dir}/anaconda3/bin:$PATH"
"""
        
        with open(profile_path, 'w') as f:
            f.write(conda_init)
        
        # Make it executable
        run_command(f"chmod +x {profile_path}")
        
        # Accept Terms of Service for default channels
        print("📋 Accepting Anaconda Terms of Service...")
        run_command(f"{base_dir}/anaconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main")
        run_command(f"{base_dir}/anaconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r")
        
        print(f"✅ Anaconda installed successfully at {base_dir}/anaconda3!")
        print("💡 You may need to restart your terminal or run: source /etc/profile")
        
        # Update conda path
        conda_path = f"{base_dir}/anaconda3/bin/conda"
    
    print(f"✅ Found conda at: {conda_path}")
    return conda_path


def create_conda_environment(study_name, python_version="3.9", base_dir="/mnt/study"):
    """Create a conda environment for the study."""
    env_name = f"{study_name.lower().replace(' ', '-')}-env"
    
    print(f"🔧 Creating conda environment: {env_name}")
    
    # Get conda path
    conda_path = f"{base_dir}/anaconda3/bin/conda"
    
    # Accept Terms of Service for default channels (in case they weren't accepted before)
    print("📋 Ensuring Anaconda Terms of Service are accepted...")
    try:
        run_command(f"{conda_path} tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main", check=False)
        run_command(f"{conda_path} tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r", check=False)
        print("✅ Terms of Service accepted")
    except Exception as e:
        print(f"⚠️  Warning: Could not accept ToS automatically: {e}")
        print("💡 This might be due to existing conda configuration")
    
    # Check if environment already exists
    env_exists = run_command(f"{conda_path} env list | grep {env_name}", check=False, capture_output=True)
    
    if env_exists:
        print(f"⚠️  Environment {env_name} already exists. Removing it...")
        run_command(f"{conda_path} env remove -n {env_name} -y")
    
    # Create new environment
    run_command(f"{conda_path} create -n {env_name} python={python_version} -y")
    
    print(f"✅ Created conda environment: {env_name}")
    return env_name


def install_packages(env_name, study_path, base_dir="/mnt/study"):
    """Install required packages in the conda environment."""
    print(f"📦 Installing packages in {env_name}")
    
    # Get conda path
    conda_path = f"{base_dir}/anaconda3/bin/conda"
    
    # Activate environment and install packages
    conda_packages = [
        "flask",
        "flask-restful", 
        "pymongo",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "python-dotenv",
        "requests"
    ]
    
    for package in conda_packages:
        print(f"  Installing {package}...")
        run_command(f"{conda_path} run -n {env_name} pip install {package}")
    
    # Install the study framework core in editable mode for easy updates
    print("  Installing study-framework-core in editable mode...")
    run_command(f"{conda_path} run -n {env_name} pip install -e study_framework_core/")
    
    # Install gunicorn
    print("  Installing gunicorn...")
    run_command(f"{conda_path} run -n {env_name} pip install gunicorn")
    
    print("✅ All packages installed successfully")


def create_directory_structure(study_name, base_dir, user):
    """Create the directory structure for the study."""
    study_dir = Path(base_dir) / study_name.lower().replace(' ', '-')
    
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


def create_systemd_service(study_name, env_name, study_dir, user, base_dir):
    """Create separate systemd services for API and internal web."""
    api_service_name = f"{study_name.lower().replace(' ', '-')}-api"
    internal_service_name = f"{study_name.lower().replace(' ', '-')}-internal"
    
    # Create socket directory
    socket_dir = "/var/sockets"
    run_command(f"mkdir -p {socket_dir}")
    run_command(f"chown {user}:www-data {socket_dir}")
    run_command(f"chmod 755 {socket_dir}")
    
    # Get conda environment path using full conda path
    conda_path = f"{base_dir}/anaconda3/bin/conda"
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


def create_nginx_config(study_name, api_service_name, internal_service_name):
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
        # Allow all IPs for testing (customize as needed for production)
        # allow 129.10.0.0/16;
        # allow 129.10.128.0/17;
        # allow 129.10.64.0/18;
        # allow 155.33.0.0/16;
        # allow 155.33.0.0/17;
        # allow 10.0.0.0/8;
        # deny all;

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
    
    # Test nginx configuration
    if run_command("nginx -t", check=False):
        print("✅ Nginx configuration is valid")
        run_command("systemctl reload nginx")
    else:
        print("❌ Nginx configuration is invalid. Please check the configuration.")
    
    return nginx_file


def create_wsgi_files(study_dir, study_name, user):
    """Create separate WSGI files for API and internal web."""
    
    # API WSGI file (Priority #1 - Data Collection)
    api_wsgi_content = f"""#!/usr/bin/env python3
\"\"\"
API WSGI entry point for {study_name} (Data Collection - Priority #1)
\"\"\"

import sys
import os
from pathlib import Path

# Add the study directory to Python path
study_path = Path(__file__).parent
sys.path.insert(0, str(study_path))

# Debug: Print current working directory and Python path
print(f"Current working directory: {{os.getcwd()}}")
print(f"Study path: {{study_path}}")
print(f"Python path: {{sys.path}}")

# Check if core framework exists
core_path = study_path / "study_framework_core"
print(f"Core framework path exists: {{core_path.exists()}}")

try:
    print("Attempting to import study_framework_core.core.config...")
    from study_framework_core.core.config import set_config_file
    print("✅ Successfully imported config")
    
    print("Attempting to import Flask...")
    from flask import Flask
    print("✅ Successfully imported Flask")
    
    print("Attempting to import flask_restful...")
    from flask_restful import Api
    print("✅ Successfully imported flask_restful")
    
    print("Attempting to import CoreAPIEndpoints...")
    from study_framework_core.core.api import CoreAPIEndpoints
    print("✅ Successfully imported CoreAPIEndpoints")
    
    # Load configuration
    config_file = study_path / "config" / "study_config.json"
    print(f"Config file path: {{config_file}}")
    print(f"Config file exists: {{config_file.exists()}}")
    set_config_file(str(config_file))
    print("✅ Configuration loaded")
    
    # Create API-only app
    app = Flask(__name__)
    api = Api(app, prefix='/api/v1')
    print("✅ Flask app created")
    
    # Get auth key from config
    from study_framework_core.core.config import get_config
    config = get_config()
    auth_key = config.security.auth_key
    print("✅ Auth key retrieved from config")
    
    # Setup core API routes
    core_api = CoreAPIEndpoints(api, auth_key)
    print("✅ Core API routes setup")
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        return dict(status='healthy', service='study-framework-api')
    
    print("✅ API WSGI setup complete")
        
except Exception as e:
    print(f"❌ Error in API WSGI: {{e}}")
    import traceback
    traceback.print_exc()
    # Create a minimal app for debugging
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/health')
    def health_check():
        return dict(status='error', message=str(e))
    
    @app.route('/')
    def debug():
        return dict(status='debug', error=str(e))

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

# Add the study directory to Python path
study_path = Path(__file__).parent
sys.path.insert(0, str(study_path))

# Debug: Print current working directory and Python path
print(f"Current working directory: {{os.getcwd()}}")
print(f"Study path: {{study_path}}")
print(f"Python path: {{sys.path}}")

# Check if core framework exists
core_path = study_path / "study_framework_core"
print(f"Core framework path exists: {{core_path.exists()}}")

try:
    print("Attempting to import study_framework_core.core.config...")
    from study_framework_core.core.config import set_config_file
    print("✅ Successfully imported config")
    
    print("Attempting to import InternalWebBase...")
    from study_framework_core.core.internal_web import InternalWebBase
    print("✅ Successfully imported InternalWebBase")
    
    print("Attempting to import DashboardBase...")
    from study_framework_core.core.dashboard import DashboardBase
    print("✅ Successfully imported DashboardBase")
    
    # Load configuration
    config_file = study_path / "config" / "study_config.json"
    print(f"Config file path: {{config_file}}")
    print(f"Config file exists: {{config_file.exists()}}")
    set_config_file(str(config_file))
    print("✅ Configuration loaded")
    
    # Create internal web app with multiple template directories
    from flask import Flask
    app = Flask(__name__)
    
    # Configure template directories (core first, then study-specific for overrides)
    core_templates = study_path / "study_framework_core" / "templates"
    study_templates = study_path / "templates"
    
    # Create study templates directory if it doesn't exist
    study_templates.mkdir(exist_ok=True)
    
    # Set up template loader to look in both directories
    from jinja2 import ChoiceLoader, FileSystemLoader
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(str(study_templates)),  # Study-specific templates (override core)
        FileSystemLoader(str(core_templates)),   # Core templates (fallback)
    ])
    
    print("✅ Flask app created with dual template directories")
    print(f"   Core templates: {core_templates}")
    print(f"   Study templates: {study_templates}")
    
    # Create a concrete dashboard implementation
    class SimpleDashboard(DashboardBase):
        def _get_custom_columns(self):
            return []  # No custom columns for basic setup
        
        def generate_custom_row_data(self, user_data, date_str):
            return dict()  # No custom data for basic setup
    
    # Setup internal web routes
    dashboard = SimpleDashboard()
    internal_web = InternalWebBase(app, dashboard)
    print("✅ Internal web routes setup")
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        return dict(status='healthy', service='study-framework-internal')
    
    print("✅ Internal Web WSGI setup complete")
        
except Exception as e:
    print(f"❌ Error in Internal Web WSGI: {{e}}")
    import traceback
    traceback.print_exc()
    # Create a minimal app for debugging
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/health')
    def health_check():
        return dict(status='error', message=str(e))
    
    @app.route('/')
    def debug():
        return dict(status='debug', error=str(e))

if __name__ == "__main__":
    app.run()
"""
    
    internal_wsgi_file = study_dir / "internal_wsgi.py"
    
    print(f"🐍 Creating internal web WSGI file: {internal_wsgi_file}")
    
    with open(internal_wsgi_file, 'w') as f:
        f.write(internal_wsgi_content)
    
    # Make both executable and set ownership
    run_command(f"chmod +x {api_wsgi_file}")
    run_command(f"chmod +x {internal_wsgi_file}")
    run_command(f"chown {user}:{user} {api_wsgi_file}")
    run_command(f"chown {user}:{user} {internal_wsgi_file}")
    
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


def create_admin_user(study_dir: Path, db_username: str, db_password: str, db_host: str, db_port: str, db_name: str, base_dir: str = "/mnt/study"):
    """Create admin user for internal web access."""
    try:
        # Use conda environment to run the admin user creation
        conda_path = f"{base_dir}/anaconda3/bin/conda"
        study_name = study_dir.name
        env_name = f"{study_name}-env"
        
        # Create a Python script to create the admin user
        admin_script = study_dir / "create_admin.py"
        admin_script_content = f"""#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Set up environment
os.environ['STUDY_CONFIG_FILE'] = str(Path(__file__).parent / "config" / "study_config.json")
sys.path.insert(0, str(Path(__file__).parent))

try:
    from study_framework_core.core.handlers import create_admin_user
    result = create_admin_user()
    
    if result['success']:
        print(f"SUCCESS:{{result['username']}}:{{result['password']}}")
    else:
        print(f"ERROR:{{result['error']}}")
except Exception as e:
    print(f"EXCEPTION:{{str(e)}}")
"""
        
        with open(admin_script, 'w') as f:
            f.write(admin_script_content)
        
        # Run the script in the conda environment
        result = run_command(f"{conda_path} run -n {env_name} python {admin_script}", capture_output=True)
        
        # Parse the result
        if result and result.startswith("SUCCESS:"):
            parts = result.split(":")
            username = parts[1]
            password = parts[2]
            print(f"✅ Admin user created successfully!")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"   ⚠️  Please save this password securely!")
            
            # Clean up the script
            admin_script.unlink()
            return password
        else:
            error_msg = result.replace("ERROR:", "").replace("EXCEPTION:", "") if result else "Unknown error"
            print(f"❌ Failed to create admin user: {error_msg}")
            
            # Clean up the script
            admin_script.unlink()
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


def copy_core_framework(study_dir: Path, user: str):
    """Copy the core framework package to the study directory."""
    try:
        # Get the path to the core framework
        core_framework_dir = Path(__file__).parent / "study_framework_core"
        study_core_dir = study_dir / "study_framework_core"
        
        if core_framework_dir.exists():
            print(f"📦 Copying core framework to {study_core_dir}")
            
            # Copy the entire study_framework_core directory
            shutil.copytree(core_framework_dir, study_core_dir, dirs_exist_ok=True)
            
            # Make sure the package is properly set up
            init_file = study_core_dir / "__init__.py"
            if not init_file.exists():
                init_file.touch()
            
            # Set ownership immediately after copying
            run_command(f"chown -R {user}:{user} {study_core_dir}")
            
            print(f"✅ Core framework copied successfully")
        else:
            print(f"❌ Error: Core framework directory not found: {core_framework_dir}")
            
    except Exception as e:
        print(f"❌ Error copying core framework: {e}")
        raise


def create_study_config(study_name: str, study_dir: Path, db_username: str, db_password: str, 
                       db_host: str, db_port: str, db_name: str, auth_key: str, announcement_key: str, user: str) -> Dict[str, Any]:
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
    
    # Set ownership
    run_command(f"chown {user}:{user} {config_file}")
    
    return config_content


def create_requirements_file(study_dir):
    """Create requirements.txt file."""
    requirements_content = """# Study Framework Core
git+https://github.com/UbiWell/ubiwell-study-backend-core.git

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


def update_core_framework(study_name, base_dir="/mnt/study"):
    """Update the core framework to the latest version."""
    env_name = f"{study_name.lower().replace(' ', '-')}-env"
    
    print(f"🔄 Updating core framework in {env_name}")
    
    # Get conda path
    conda_path = f"{base_dir}/anaconda3/bin/conda"
    
    # Update the core package
    run_command(f"{conda_path} run -n {env_name} pip install --upgrade -e study_framework_core/")
    
    print("✅ Core framework updated successfully!")
    print("💡 You may need to restart the services:")
    print(f"   sudo systemctl restart {study_name.lower().replace(' ', '-')}-api")
    print(f"   sudo systemctl restart {study_name.lower().replace(' ', '-')}-internal")


def main():
    parser = argparse.ArgumentParser(description='Setup a new study with conda, systemd, and nginx')
    parser.add_argument('study_name', help='Name of the study')
    parser.add_argument('--user', default='connect', help='System user to run the service')
    parser.add_argument('--base-dir', default='/mnt/study', help='Base directory for studies')
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
        update_core_framework(args.study_name, args.base_dir)
        return
    
    print(f"🚀 Setting up study: {args.study_name}")
    print(f"👤 User: {args.user}")
    print(f"📁 Base directory: {args.base_dir}")
    
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script must be run as root (use sudo)")
        sys.exit(1)
    
    # Fix conda Terms of Service issues if Anaconda is installed
    anaconda_dir = Path(args.base_dir) / "anaconda3"
    if anaconda_dir.exists():
        print("🔧 Checking conda Terms of Service...")
        fix_conda_tos(args.base_dir)
    
    # Check Anaconda installation
    conda_path = check_anaconda(args.base_dir)
    
    # Create conda environment
    env_name = create_conda_environment(args.study_name, args.python_version, args.base_dir)
    
    # Create directory structure
    study_dir = create_directory_structure(args.study_name, args.base_dir, args.user)
    
    # Copy core framework to study directory
    copy_core_framework(study_dir, args.user)
    
    # Install packages
    install_packages(env_name, Path.cwd(), args.base_dir)
    
    # Create WSGI files first (needed for systemd services)
    api_wsgi_file, internal_wsgi_file = create_wsgi_files(study_dir, args.study_name, args.user)
    
    # Create systemd services (after WSGI files exist)
    api_service_name, internal_service_name = create_systemd_service(args.study_name, env_name, study_dir, args.user, args.base_dir)
    
    # Create nginx configuration (after services are created)
    nginx_file = create_nginx_config(args.study_name, api_service_name, internal_service_name)
    
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
        args.announcement_key or 'study123',
        args.user
    )
    
    # Create admin user for internal web access
    admin_password = create_admin_user(
        study_dir,
        args.db_username or 'study_user',
        args.db_password or 'study_password',
        args.db_host or 'localhost',
        args.db_port or '27017',
        args.db_name,
        args.base_dir
    )
    requirements_file = create_requirements_file(study_dir)
    readme_file = create_readme(study_dir, args.study_name, api_service_name)
    
    # Set proper ownership for all created files and directories
    print(f"🔐 Setting ownership for all files to {args.user}:{args.user}")
    
    # Set ownership for study directory and all contents
    run_command(f"chown -R {args.user}:{args.user} {study_dir}")
    
    # Set ownership for Anaconda installation (if it was created)
    anaconda_dir = Path(args.base_dir) / "anaconda3"
    if anaconda_dir.exists():
        print(f"🔐 Setting ownership for Anaconda installation")
        run_command(f"chown -R {args.user}:{args.user} {anaconda_dir}")
    
    # Set ownership for base directory (but keep root for system files)
    base_dir = Path(args.base_dir)
    if base_dir.exists():
        # Set ownership for study-related directories only
        for item in base_dir.iterdir():
            if item.name.startswith(f"{args.study_name.lower().replace(' ', '-')}"):
                run_command(f"chown -R {args.user}:{args.user} {item}")
    
    print(f"✅ Ownership set successfully")
    
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
