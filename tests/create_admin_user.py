#!/usr/bin/env python3
"""
Standalone script to create admin user for internal web access.
"""

import os
import sys
from pathlib import Path

def main():
    # Get the study directory (parent of this script)
    script_dir = Path(__file__).parent
    study_dir = script_dir.parent
    
    print(f"🔐 Creating admin user for study: {study_dir.name}")
    
    # Check if we're in a conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if not conda_env:
        print("❌ Not in a conda environment!")
        print("💡 Please activate the conda environment first:")
        print(f"   conda activate bean-study-env")
        sys.exit(1)
    
    print(f"✅ Using conda environment: {conda_env}")
    
    # Add the submodule to Python path
    submodule_path = study_dir / "ubiwell-study-backend-core"
    if not submodule_path.exists():
        print(f"❌ Submodule not found: {submodule_path}")
        sys.exit(1)
    
    sys.path.insert(0, str(submodule_path))
    
    # Set environment variable for config
    config_file = study_dir / "config" / "study_config.json"
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    
    os.environ['STUDY_CONFIG_FILE'] = str(config_file)
    
    try:
        from study_framework_core.core.handlers import create_admin_user
        
        result = create_admin_user()
        
        if result['success']:
            print(f"✅ Admin user created successfully!")
            print(f"   Username: {result['username']}")
            print(f"   Password: {result['password']}")
            print(f"   ⚠️  Please save this password securely!")
        else:
            print(f"❌ Failed to create admin user: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        print(f"💡 Make sure you're running this from the study directory")
        print(f"💡 Make sure the conda environment is activated")
        sys.exit(1)

if __name__ == "__main__":
    main()
