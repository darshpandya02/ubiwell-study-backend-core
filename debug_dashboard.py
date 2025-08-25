#!/usr/bin/env python3
"""
Debug script to test dashboard functionality.
Run this from the study directory.
"""

import os
import sys
from pathlib import Path

def debug_dashboard():
    """Debug dashboard functionality step by step."""
    study_dir = Path.cwd()
    
    # Set up environment
    config_file = study_dir / "config" / "study_config.json"
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        return
    
    os.environ['STUDY_CONFIG_FILE'] = str(config_file)
    sys.path.insert(0, str(study_dir))
    
    try:
        print("🔍 Step 1: Importing config...")
        from study_framework_core.core.config import get_config
        config = get_config()
        print("✅ Config loaded")
        print(f"   Database: {config.database.host}:{config.database.port}")
        print(f"   Database name: {config.database.database}")
        
        print("🔍 Step 2: Testing database connection...")
        from study_framework_core.core.handlers import get_db
        db = get_db()
        print("✅ Database connection successful")
        
        print("🔍 Step 3: Testing collections...")
        collections = db.list_collection_names()
        print(f"✅ Available collections: {collections}")
        
        print("🔍 Step 4: Testing dashboard imports...")
        from study_framework_core.core.dashboard import DashboardBase
        
        class TestDashboard(DashboardBase):
            def _get_custom_columns(self):
                return []
            
            def generate_custom_row_data(self, user_data, date_str):
                return dict()
        
        dashboard = TestDashboard()
        print("✅ Dashboard class created successfully")
        
        print("🔍 Step 5: Testing dashboard methods...")
        columns = dashboard.get_all_columns()
        print(f"✅ Dashboard columns: {[col.name for col in columns]}")
        
        print("🔍 Step 6: Testing template rendering...")
        from flask import Flask
        from jinja2 import ChoiceLoader, FileSystemLoader
        
        app = Flask(__name__)
        
        # Configure template directories
        core_templates = study_dir / "study_framework_core" / "templates"
        study_templates = study_dir / "templates"
        
        app.jinja_loader = ChoiceLoader([
            FileSystemLoader(str(study_templates)),
            FileSystemLoader(str(core_templates)),
        ])
        
        with app.app_context():
            try:
                template = app.jinja_env.get_template('dashboard_base.html')
                print("✅ Dashboard template found")
            except Exception as e:
                print(f"❌ Dashboard template error: {e}")
                # List available templates
                print("Available templates:")
                for template_dir in [study_templates, core_templates]:
                    if template_dir.exists():
                        for template_file in template_dir.glob("*.html"):
                            print(f"   {template_file}")
        
        print("✅ Dashboard debug completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in dashboard debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dashboard()

