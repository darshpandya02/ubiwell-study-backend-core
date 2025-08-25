#!/usr/bin/env python3
"""
Debug script to identify the quote_from_bytes error.
Run this from the study directory.
"""

import os
import sys
from pathlib import Path

def debug_admin_user():
    """Debug admin user creation step by step."""
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
        print("🔍 Step 1: Importing config...")
        from study_framework_core.core.config import set_config_file
        print("✅ Config imported")
        
        print("🔍 Step 2: Setting config file...")
        set_config_file(str(config_file))
        print("✅ Config file set")
        
        print("🔍 Step 3: Importing handlers...")
        from study_framework_core.core.handlers import create_admin_user, generate_password
        print("✅ Handlers imported")
        
        print("🔍 Step 4: Testing password generation...")
        try:
            password = generate_password(12)
            print(f"✅ Password generated: {password}")
        except Exception as e:
            print(f"❌ Password generation failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("🔍 Step 5: Creating admin user...")
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
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_admin_user()

