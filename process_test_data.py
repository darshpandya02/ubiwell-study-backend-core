#!/usr/bin/env python3
"""
Process Test Data Script

This script processes uploaded test data on the server.
Run this on the server after data has been uploaded.

Usage:
    python process_test_data.py --user test130
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from study_framework_core.core.config import get_config
from study_framework_core.core.handlers import get_db
from study_framework_core.core.processing_scripts import DataProcessor


class TestDataProcessor:
    """Process uploaded test data on the server."""
    
    def __init__(self, user_id: str):
        self.config = get_config()
        self.db = get_db()
        self.user_id = user_id
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_user_exists(self) -> bool:
        """Check if the test user exists in the database."""
        self.log("Checking if test user exists...")
        
        user = self.db['users'].find_one({'uid': self.user_id})
        if user:
            self.log(f"✅ User {self.user_id} exists in database")
            return True
        else:
            self.log(f"❌ User {self.user_id} not found in database", "ERROR")
            self.log("Please run the upload script first to create the user and upload data.")
            return False
    
    def check_uploaded_files(self) -> bool:
        """Check if files have been uploaded for the user."""
        self.log("Checking for uploaded files...")
        
        # Check various upload directories
        upload_paths = [
            self.config.paths.data_upload_path,
            self.config.paths.data_processed_path,
            self.config.paths.ema_file_path,
            self.config.paths.active_sensing_upload_path
        ]
        
        total_files = 0
        for upload_path in upload_paths:
            if upload_path and os.path.exists(upload_path):
                user_dir = os.path.join(upload_path, self.user_id)
                if os.path.exists(user_dir):
                    files = list(Path(user_dir).rglob("*"))
                    if files:
                        self.log(f"  Found {len(files)} files in {upload_path}")
                        total_files += len(files)
        
        if total_files > 0:
            self.log(f"✅ Found {total_files} uploaded files for user {self.user_id}")
            return True
        else:
            self.log(f"❌ No uploaded files found for user {self.user_id}", "ERROR")
            self.log("Please run the upload script first to upload data.")
            return False
    
    def process_phone_data(self) -> bool:
        """Process phone data for the test user."""
        self.log("Processing phone data...")
        
        processor = DataProcessor()
        success = processor.process_phone_data(self.user_id)
        
        if success:
            self.log("✅ Phone data processing completed")
        else:
            self.log("❌ Phone data processing failed", "ERROR")
        
        return success
    
    def process_garmin_data(self) -> bool:
        """Process Garmin data for the test user."""
        self.log("Processing Garmin data...")
        
        processor = DataProcessor()
        
        # Look for Garmin FIT files in upload directories
        upload_paths = [
            self.config.paths.data_upload_path,
            self.config.paths.data_processed_path
        ]
        
        garmin_files = []
        for upload_path in upload_paths:
            if upload_path and os.path.exists(upload_path):
                user_dir = os.path.join(upload_path, self.user_id)
                if os.path.exists(user_dir):
                    fit_files = list(Path(user_dir).rglob("*.fit"))
                    garmin_files.extend(fit_files)
        
        if not garmin_files:
            self.log("⚠️ No Garmin FIT files found")
            return True
        
        success_count = 0
        for garmin_file in garmin_files:
            self.log(f"Processing: {garmin_file.name}")
            success = processor.process_garmin_fit_file(
                user=self.user_id,
                input_file=str(garmin_file)
            )
            if success:
                success_count += 1
                self.log(f"✅ Processed: {garmin_file.name}")
            else:
                self.log(f"❌ Failed: {garmin_file.name}", "ERROR")
        
        self.log(f"✅ Processed {success_count}/{len(garmin_files)} Garmin files")
        return success_count > 0
    
    def generate_summaries(self) -> bool:
        """Generate daily summaries for the test user."""
        self.log("Generating daily summaries...")
        
        processor = DataProcessor()
        success = processor.generate_daily_summaries(hours_back=24)
        
        if success:
            self.log("✅ Daily summaries generated")
            
            # Show summary data
            summary = self.db['daily_summaries'].find_one({'uid': self.user_id})
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
    
    def check_database_data(self) -> bool:
        """Check what data is in the database for the test user."""
        self.log("Checking database data...")
        
        collections_to_check = [
            'location_data',
            'activity_data',
            'steps_data',
            'battery_data',
            'wifi_data',
            'bluetooth_data',
            'brightness_data',
            'garmin_hr_data',
            'garmin_stress_data',
            'garmin_steps_data',
            'garmin_respiration_data',
            'garmin_ibi_data',
            'accelerometer_data',
            'calllog_data',
            'lock_unlock_data',
            'ema_data',
            'ema_status_data',
            'notification_data',
            'app_usage_data',
            'daily_diary_data',
            'daily_summaries',
            'unknown_events_data'
        ]
        
        total_records = 0
        for collection_name in collections_to_check:
            count = self.db[collection_name].count_documents({'uid': self.user_id})
            if count > 0:
                self.log(f"  {collection_name}: {count} records")
                total_records += count
            else:
                self.log(f"  {collection_name}: 0 records")
        
        self.log(f"Total records for {self.user_id}: {total_records}")
        
        if total_records > 0:
            self.log("✅ Data found in database")
        else:
            self.log("❌ No data found in database", "ERROR")
        
        return total_records > 0
    
    def cleanup_test_data(self) -> bool:
        """Clean up all test data for the user."""
        self.log("Cleaning up test data...")
        
        # Remove test user
        result = self.db['users'].delete_one({'uid': self.user_id})
        if result.deleted_count > 0:
            self.log(f"✅ Removed user: {self.user_id}")
        else:
            self.log(f"⚠️ User {self.user_id} not found")
        
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
            result = self.db[collection_name].delete_many({'uid': self.user_id})
            if result.deleted_count > 0:
                self.log(f"✅ Deleted {result.deleted_count} records from {collection_name}")
                total_deleted += result.deleted_count
        
        self.log(f"Total records deleted: {total_deleted}")
        
        # Remove uploaded files
        upload_paths = [
            self.config.paths.data_upload_path,
            self.config.paths.data_processed_path,
            self.config.paths.ema_file_path,
            self.config.paths.active_sensing_upload_path
        ]
        
        for upload_path in upload_paths:
            if upload_path and os.path.exists(upload_path):
                user_dir = os.path.join(upload_path, self.user_id)
                if os.path.exists(user_dir):
                    import shutil
                    shutil.rmtree(user_dir)
                    self.log(f"✅ Removed uploaded files: {user_dir}")
        
        self.log("✅ Cleanup completed")
        return True
    
    def run_processing(self) -> bool:
        """Run the complete processing pipeline."""
        self.log("Starting test data processing...")
        self.log("=" * 60)
        
        steps = [
            ("Check user exists", self.check_user_exists),
            ("Check uploaded files", self.check_uploaded_files),
            ("Process phone data", self.process_phone_data),
            ("Process Garmin data", self.process_garmin_data),
            ("Generate summaries", self.generate_summaries),
            ("Check database data", self.check_database_data),
        ]
        
        # Run all steps
        for step_name, step_func in steps:
            self.log(f"\n--- {step_name} ---")
            if not step_func():
                self.log(f"Processing failed at step: {step_name}", "ERROR")
                return False
        
        self.log("\n" + "=" * 60)
        self.log("Processing completed successfully!")
        self.log("Data is now available in the dashboard.")
        self.log("You can view it at: http://localhost/internal_web/")
        
        # Ask user if they want to cleanup
        response = input("\nDo you want to cleanup test data? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            self.log("\n--- Cleanup ---")
            self.cleanup_test_data()
            self.log("Test completed and cleaned up.")
        else:
            self.log("Test completed. Test data remains for manual inspection.")
        
        return True


def main():
    """Main function to run the processing."""
    parser = argparse.ArgumentParser(description='Process uploaded test data')
    parser.add_argument('--user', default='test130', help='User ID to process (default: test130)')
    parser.add_argument('--cleanup', action='store_true', help='Automatically cleanup test data after processing')
    
    args = parser.parse_args()
    
    print("Test Data Processing Script")
    print("=" * 40)
    print(f"User ID: {args.user}")
    print()
    
    # Create and run processor
    processor = TestDataProcessor(args.user)
    success = processor.run_processing()
    
    if args.cleanup and success:
        processor.cleanup_test_data()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
