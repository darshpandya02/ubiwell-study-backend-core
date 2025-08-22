#!/usr/bin/env python3
"""
Step-by-Step Pipeline Test Script

This script allows testing individual components of the pipeline for debugging.
Run individual functions to test specific parts of the system.
"""

import os
import sys
import json
import zipfile
import shutil
import requests
import time
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
from typing import Dict, List, Optional

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up environment for config loading
config_file = project_root / "config" / "study_config.json"
if config_file.exists():
    os.environ['STUDY_CONFIG_FILE'] = str(config_file)
    print(f"Set STUDY_CONFIG_FILE to: {config_file}")
else:
    print(f"Warning: Config file not found at {config_file}")

from study_framework_core.core.config import get_config
from study_framework_core.core.handlers import get_db, create_user
from study_framework_core.core.processing_scripts import DataProcessor


class StepByStepTester:
    """Step-by-step pipeline tester for debugging."""
    
    def __init__(self):
        self.config = get_config()
        self.db = get_db()
        self.test_user = "test130"
        self.test_data_dir = project_root / "test_data"
        self.api_base_url = "http://localhost/api/v1"
        self.user_credentials = None
        
        # Debug: Print config paths
        print(f"DEBUG: Config data_upload_path: {self.config.paths.data_upload_path}")
        print(f"DEBUG: Config base_dir: {self.config.paths.base_dir}")
        print(f"DEBUG: Expected upload path: {Path(self.config.paths.data_upload_path) / 'phone' / self.test_user}")
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        self.log("Checking prerequisites...")
        
        # Check if test file exists
        test_file = project_root / "test_file.zip"
        if not test_file.exists():
            self.log(f"❌ Test file not found: {test_file}", "ERROR")
            return False
        
        # Check if API server is running
        try:
            response = requests.get("http://localhost/api/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ API server is running")
            else:
                self.log("⚠️ API server responded but not healthy", "WARNING")
        except requests.exceptions.RequestException:
            self.log("❌ API server is not running", "ERROR")
            self.log("Please start the API server first")
            return False
        
        # Check database connection
        try:
            # Try to access database
            user_count = self.db['users'].count_documents({})
            self.log(f"✅ Database connection successful (found {user_count} users)")
        except Exception as e:
            self.log(f"❌ Database connection failed: {e}", "ERROR")
            return False
        
        self.log("✅ All prerequisites met")
        return True
    
    def unzip_test_data(self):
        """Unzip the test data file."""
        self.log("Unzipping test data...")
        
        test_file = project_root / "test_file.zip"
        
        # Create test data directory
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Unzip the file
        with zipfile.ZipFile(test_file, 'r') as zip_ref:
            zip_ref.extractall(self.test_data_dir)
        
        # List extracted files
        files = list(self.test_data_dir.rglob("*"))
        self.log(f"✅ Extracted {len(files)} files to {self.test_data_dir}")
        
        # Show file structure
        for file in files[:10]:
            self.log(f"  - {file.relative_to(self.test_data_dir)}")
        if len(files) > 10:
            self.log(f"  ... and {len(files) - 10} more files")
        
        return True
    
    def create_test_user(self):
        """Create test user in database."""
        self.log("Creating test user...")
        
        # Check if user already exists
        existing_user = self.db['users'].find_one({'uid': self.test_user})
        if existing_user:
            self.log(f"⚠️ User {self.test_user} already exists")
            return True
        
        # Create user
        result = create_user(self.test_user, email=f"{self.test_user}@test.com")
        
        if result['success']:
            self.user_credentials = result['user']
            self.log(f"✅ Created user: {self.test_user}")
            self.log(f"  Study Password: {self.user_credentials['study_pass']}")
            self.log(f"  Garmin Password: {self.user_credentials['garmin_pass']}")
            self.log(f"  UID Code: {self.user_credentials['uid_code']}")
            return True
        else:
            self.log(f"❌ Failed to create user: {result.get('error', 'Unknown error')}", "ERROR")
            return False
    
    def upload_single_file(self, file_path: Path):
        """Upload a single file to the API."""
        if not self.user_credentials:
            self.log("❌ No user credentials available", "ERROR")
            return False
        
        try:
            url = f"{self.api_base_url}/upload_file"
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                data = {
                    'uid': self.test_user,
                    'token': self.user_credentials['study_pass']
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        self.log(f"✅ Uploaded: {file_path.name}")
                        return True
                    else:
                        self.log(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    self.log(f"❌ Upload failed with status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Error uploading {file_path.name}: {e}")
            return False
    
    def upload_all_files(self):
        """Upload all data files to API."""
        self.log("Uploading all files to API...")
        
        # Find all data files
        data_files = []
        for file_path in self.test_data_dir.rglob("*"):
            if file_path.is_file():
                file_name = file_path.name.lower()
                if any(ext in file_name for ext in ['.db', '.json', '.fit', '.csv']):
                    data_files.append(file_path)
        
        self.log(f"Found {len(data_files)} files to upload")
        
        # Upload each file
        success_count = 0
        for file_path in data_files:
            if self.upload_single_file(file_path):
                success_count += 1
        
        self.log(f"✅ Uploaded {success_count}/{len(data_files)} files successfully")
        return success_count > 0
    
    def _setup_environment(self):
        """Set up the environment for processing."""
        # Set the STUDY_CONFIG_FILE environment variable if not already set
        if 'STUDY_CONFIG_FILE' not in os.environ:
            # Try to find the config file in common locations
            import os
            from pathlib import Path
            
            # Look for config file in current directory or parent directories
            current_dir = Path.cwd()
            config_file = None
            
            # Check current directory
            if (current_dir / "config" / "study_config.json").exists():
                config_file = current_dir / "config" / "study_config.json"
            # Check parent directories
            else:
                for parent in current_dir.parents:
                    if (parent / "config" / "study_config.json").exists():
                        config_file = parent / "config" / "study_config.json"
                        break
            
            if config_file:
                os.environ['STUDY_CONFIG_FILE'] = str(config_file)
                self.log(f"Set STUDY_CONFIG_FILE to: {config_file}")
                
                # Reload the configuration with the new file
                from study_framework_core.core.config import set_config_file
                set_config_file(str(config_file))
            else:
                self.log("Warning: Could not find study_config.json. Using default configuration.")
    
    def process_phone_data(self):
        """Process phone data."""
        self.log("Processing phone data...")
        
        self._setup_environment()
        processor = DataProcessor()
        success = processor.process_phone_data(self.test_user)
        
        if success:
            self.log("✅ Phone data processing completed")
        else:
            self.log("❌ Phone data processing failed", "ERROR")
        
        return success
    
    def process_garmin_data(self):
        """Process Garmin data."""
        self.log("Processing Garmin data...")
        
        self._setup_environment()
        processor = DataProcessor()
        success = processor.process_garmin_data(self.test_user)
        
        if success:
            self.log("✅ Garmin data processing completed")
        else:
            self.log("❌ Garmin data processing failed", "ERROR")
        
        return success
    
    def generate_summaries(self):
        """Generate daily summaries."""
        self.log("Generating daily summaries...")
        
        self._setup_environment()
        processor = DataProcessor()
        success = processor.generate_daily_summaries(hours_back=24)
        
        if success:
            self.log("✅ Daily summaries generated")
            
            # Show summary data
            config = get_config()
            summary = self.db[config.collections.DAILY_SUMMARY].find_one({'uid': self.test_user})
            if summary:
                self.log("Summary data:")
                self.log(f"  Date: {summary.get('date_str', 'N/A')}")
                self.log(f"  Location duration: {summary.get('location', {}).get('duration_hours', 0):.2f} hours")
                self.log(f"  Garmin wear duration: {summary.get('garmin_wear_duration', 0):.2f} hours")
                self.log(f"  Garmin on duration: {summary.get('garmin_on_duration', 0):.2f} hours")
                self.log(f"  Distance traveled: {summary.get('location', {}).get('distance_traveled', 0):.2f} meters")
                self.log(f"  EMA responses: {summary.get('ema', {}).get('response_count', 0)}")
            else:
                self.log("⚠️ No summary data found")
        else:
            self.log("❌ Failed to generate summaries", "ERROR")
        
        return success
    
    def check_database_data(self):
        """Check what data is in the database."""
        self.log("Checking database data...")
        
        config = get_config()
        collections_to_check = [
            config.collections.IOS_LOCATION,
            config.collections.IOS_ACTIVITY,
            config.collections.IOS_STEPS,
            config.collections.IOS_BATTERY,
            config.collections.IOS_WIFI,
            config.collections.IOS_BLUETOOTH,
            config.collections.IOS_BRIGHTNESS,
            config.collections.GARMIN_HR,
            config.collections.GARMIN_STRESS,
            config.collections.GARMIN_STEPS,
            config.collections.GARMIN_RESPIRATION,
            config.collections.GARMIN_IBI,
            config.collections.IOS_ACCELEROMETER,
            config.collections.IOS_CALLLOG,
            config.collections.IOS_LOCK_UNLOCK,
            config.collections.EMA_RESPONSE,
            config.collections.EMA_STATUS_EVENTS,
            config.collections.NOTIFICATION_EVENTS,
            config.collections.APP_USAGE_LOGS,
            config.collections.DAILY_SUMMARY,
            config.collections.UNKNOWN_EVENTS
        ]
        
        total_records = 0
        for collection_name in collections_to_check:
            count = self.db[collection_name].count_documents({'uid': self.test_user})
            if count > 0:
                self.log(f"  {collection_name}: {count} records")
                total_records += count
            else:
                self.log(f"  {collection_name}: 0 records")
        
        self.log(f"Total records for {self.test_user}: {total_records}")
        
        if total_records > 0:
            self.log("✅ Data found in database")
        else:
            self.log("❌ No data found in database", "ERROR")
        
        return total_records > 0
    
    def cleanup_test_data(self):
        """Clean up all test data."""
        self.log("Cleaning up test data...")
        
        # Remove test user
        result = self.db['users'].delete_one({'uid': self.test_user})
        if result.deleted_count > 0:
            self.log(f"✅ Removed user: {self.test_user}")
        else:
            self.log(f"⚠️ User {self.test_user} not found")
        
        # Remove all data from collections
        collections_to_clean = [
            'location_data', 'activity_data', 'steps_data', 'battery_data',
            'wifi_data', 'bluetooth_data', 'brightness_data', 'garmin_hr_data',
            'garmin_stress_data', 'garmin_steps_data', 'garmin_respiration_data',
            'garmin_ibi_data', 'accelerometer_data', 'calllog_data',
            'lock_unlock_data', 'ema_data', 'ema_status_data', 'notification_data',
            'app_usage_data', 'daily_diary_data', 'daily_summaries', 'unknown_events_data'
        ]
        
        total_deleted = 0
        for collection_name in collections_to_clean:
            result = self.db[collection_name].delete_many({'uid': self.test_user})
            if result.deleted_count > 0:
                self.log(f"✅ Deleted {result.deleted_count} records from {collection_name}")
                total_deleted += result.deleted_count
        
        self.log(f"Total records deleted: {total_deleted}")
        
        # Remove test data directory
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
            self.log(f"✅ Removed test data directory: {self.test_data_dir}")
        
        self.log("✅ Cleanup completed")
        return True


def show_menu():
    """Show the interactive menu."""
    print("\n" + "="*50)
    print("Study Framework Pipeline Test - Step by Step")
    print("="*50)
    print("1. Check prerequisites")
    print("2. Unzip test data")
    print("3. Create test user")
    print("4. Upload all files to API")
    print("5. Process phone data")
    print("6. Process Garmin data")
    print("7. Generate summaries")
    print("8. Check database data")
    print("9. Cleanup test data")
    print("10. Run full pipeline")
    print("0. Exit")
    print("="*50)


def main():
    """Main interactive function."""
    print("Study Framework Pipeline Test - Step by Step")
    
    # Check if test file exists
    test_file = Path("test_file.zip")
    if not test_file.exists():
        print(f"❌ Error: test_file.zip not found in current directory")
        print("Please place test_file.zip in the same directory as this script.")
        return
    
    tester = StepByStepTester()
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (0-10): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            tester.check_prerequisites()
        elif choice == "2":
            tester.unzip_test_data()
        elif choice == "3":
            tester.create_test_user()
        elif choice == "4":
            tester.upload_all_files()
        elif choice == "5":
            tester.process_phone_data()
        elif choice == "6":
            tester.process_garmin_data()
        elif choice == "7":
            tester.generate_summaries()
        elif choice == "8":
            tester.check_database_data()
        elif choice == "9":
            tester.cleanup_test_data()
        elif choice == "10":
            print("\nRunning full pipeline...")
            if (tester.check_prerequisites() and
                tester.unzip_test_data() and
                tester.create_test_user() and
                tester.upload_all_files() and
                tester.process_phone_data() and
                tester.process_garmin_data() and
                tester.generate_summaries() and
                tester.check_database_data()):
                print("\n✅ Full pipeline completed successfully!")
                response = input("Do you want to cleanup test data? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    tester.cleanup_test_data()
            else:
                print("\n❌ Pipeline failed at some step")
        else:
            print("Invalid choice. Please enter a number between 0 and 10.")


if __name__ == "__main__":
    main()
