#!/usr/bin/env python3
"""
Script to copy templates and static files to fix the internal web.
Run this from the study directory.
"""

import shutil
from pathlib import Path
import sys

def copy_templates_and_static():
    """Copy templates and static files to the study directory."""
    study_dir = Path.cwd()
    core_dir = study_dir / "study_framework_core"
    
    if not core_dir.exists():
        print("❌ study_framework_core directory not found!")
        print("Please run this script from the study directory (e.g., /mnt/study/bean-study)")
        sys.exit(1)
    
    # Create study templates directory (for customizations)
    templates_dest = study_dir / "templates"
    templates_dest.mkdir(exist_ok=True)
    
    print(f"📁 Study templates directory ready: {templates_dest}")
    print("💡 Core templates are available in study_framework_core/templates/")
    print("💡 Study-specific templates can be added to templates/ for customization")
    
    # Copy static files
    static_src = core_dir / "static"
    static_dest = study_dir / "static"
    
    if static_src.exists():
        print(f"📁 Copying static files from {static_src} to {static_dest}")
        if static_dest.exists():
            shutil.rmtree(static_dest)
        shutil.copytree(static_src, static_dest)
        print("✅ Static files copied successfully")
    else:
        print(f"❌ Static directory not found: {static_src}")
    
    # Set ownership
    import subprocess
    study_name = study_dir.name
    user = study_name  # Assuming user name matches study name
    
    print(f"🔐 Setting ownership to {user}:{user}")
    subprocess.run(f"chown -R {user}:{user} {templates_dest}", shell=True)
    subprocess.run(f"chown -R {user}:{user} {static_dest}", shell=True)
    
    print("✅ Template fix completed!")
    print("🔄 Restart the internal web service:")
    print(f"   sudo systemctl restart {study_name}-internal")

if __name__ == "__main__":
    copy_templates_and_static()
