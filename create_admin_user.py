#!/usr/bin/env python3
"""
Standalone script to create admin user for the study.
Run this from the study directory.
"""

import os
import sys
from pathlib import Path

def create_admin_user():
    """Create admin user for the study."""
    study_dir = Path.cwd()
    
    # Set up environment
    config_file = study_dir / "config" / "study_config.json"
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        print("Please run this script from the study directory (e.g., /mnt/study/bean-study)")
        sys.exit(1)
    
    os.environ['STUDY_CONFIG_FILE'] = str(config_file)
    sys.path.insert(0, str(study_dir))
    
    try:
        from study_framework_core.core.handlers import create_admin_user as create_admin_user_handler
        
        print("🔐 Creating admin user...")
        result = create_admin_user_handler()
        
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
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_admin_user()
