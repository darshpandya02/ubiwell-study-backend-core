#!/usr/bin/env python3
"""
Script to fix WSGI files for the study.
Run this from the study directory.
"""

import sys
from pathlib import Path

def main():
    # Get the study directory (parent of this script)
    script_dir = Path(__file__).parent
    study_dir = script_dir.parent
    
    print(f"🔧 Fixing WSGI files for study: {study_dir.name}")
    
    # API WSGI file
    api_wsgi_content = f"""#!/usr/bin/env python3
\"\"\"
API WSGI entry point for {study_dir.name} (Data Collection - Priority #1)
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
    api_wsgi_file.write_text(api_wsgi_content)
    print(f"✅ Fixed API WSGI file: {api_wsgi_file}")
    
    # Internal Web WSGI file
    internal_wsgi_content = f"""#!/usr/bin/env python3
\"\"\"
Internal Web WSGI entry point for {study_dir.name} (Dashboard - Priority #2)
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
    internal_wsgi_file.write_text(internal_wsgi_content)
    print(f"✅ Fixed Internal Web WSGI file: {internal_wsgi_file}")
    
    # Make both executable
    import subprocess
    subprocess.run(['chmod', '+x', str(api_wsgi_file)])
    subprocess.run(['chmod', '+x', str(internal_wsgi_file)])
    print("✅ Made WSGI files executable")
    
    print("\n🎯 WSGI files fixed! Now restart the services:")
    print("   sudo systemctl restart bean-study-api")
    print("   sudo systemctl restart bean-study-internal")

if __name__ == "__main__":
    main()
