#!/usr/bin/env python3
"""
Upload Test Data Script

This script uploads test data from a local machine to the server.
Run this from your local machine to upload the test data.

Usage:
    python upload_test_data.py --server http://your-server.com --user test130
"""

import os
import sys
import json
import zipfile
import shutil
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class TestDataUploader:
    """Upload test data to the server."""
    
    def __init__(self, server_url: str, user_id: str):
        self.server_url = server_url.rstrip('/')
        self.user_id = user_id
        self.test_data_dir = Path("test_data")
        self.user_credentials = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        self.log("Checking prerequisites...")
        
        # Check if test file exists
        test_file = Path("test_file.zip")
        if not test_file.exists():
            self.log(f"❌ Test file not found: {test_file}", "ERROR")
            return False
        
        # Check if server is accessible
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=10)
            if response.status_code == 200:
                self.log("✅ Server is accessible")
            else:
                self.log(f"⚠️ Server responded with status {response.status_code}", "WARNING")
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Cannot connect to server: {e}", "ERROR")
            return False
        
        self.log("✅ All prerequisites met")
        return True
    
    def unzip_test_data(self) -> bool:
        """Unzip the test data file."""
        self.log("Unzipping test data...")
        
        test_file = Path("test_file.zip")
        
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
    
    def create_test_user(self) -> bool:
        """Create test user on the server."""
        self.log("Creating test user on server...")
        
        try:
            # Call the user creation endpoint
            url = f"{self.server_url}/internal_web/create_user"
            data = {
                'uid': self.user_id,
                'email': f"{self.user_id}@test.com"
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    self.user_credentials = result.get('user', {})
                    self.log(f"✅ Created user: {self.user_id}")
                    self.log(f"  Study Password: {self.user_credentials.get('study_pass', 'N/A')}")
                    self.log(f"  Garmin Password: {self.user_credentials.get('garmin_pass', 'N/A')}")
                    self.log(f"  UID Code: {self.user_credentials.get('uid_code', 'N/A')}")
                    return True
                else:
                    self.log(f"❌ Failed to create user: {result.get('error', 'Unknown error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Server error: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error creating user: {e}", "ERROR")
            return False
    
    def upload_file(self, file_path: Path) -> bool:
        """Upload a single file to the server."""
        if not self.user_credentials:
            self.log("❌ No user credentials available", "ERROR")
            return False
        
        try:
            url = f"{self.server_url}/api/v1/upload_file"
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                data = {
                    'uid': self.user_id,
                    'token': self.user_credentials['study_pass']
                }
                
                response = requests.post(url, files=files, data=data, timeout=60)
                
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
    
    def upload_all_files(self) -> bool:
        """Upload all data files to the server."""
        self.log("Uploading all files to server...")
        
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
        for i, file_path in enumerate(data_files, 1):
            self.log(f"Uploading file {i}/{len(data_files)}: {file_path.name}")
            if self.upload_file(file_path):
                success_count += 1
        
        self.log(f"✅ Uploaded {success_count}/{len(data_files)} files successfully")
        return success_count > 0
    
    def cleanup_local_files(self):
        """Clean up local test data files."""
        self.log("Cleaning up local test data...")
        
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
            self.log(f"✅ Removed local test data directory: {self.test_data_dir}")
    
    def run_upload(self) -> bool:
        """Run the complete upload process."""
        self.log("Starting test data upload...")
        self.log("=" * 60)
        
        steps = [
            ("Check prerequisites", self.check_prerequisites),
            ("Unzip test data", self.unzip_test_data),
            ("Create test user", self.create_test_user),
            ("Upload all files", self.upload_all_files),
        ]
        
        # Run all steps
        for step_name, step_func in steps:
            self.log(f"\n--- {step_name} ---")
            if not step_func():
                self.log(f"Upload failed at step: {step_name}", "ERROR")
                return False
        
        self.log("\n" + "=" * 60)
        self.log("Upload completed successfully!")
        self.log(f"User {self.user_id} has been created and data uploaded.")
        self.log("You can now run the processing script on the server.")
        
        # Ask user if they want to cleanup local files
        response = input("\nDo you want to cleanup local test data? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            self.cleanup_local_files()
            self.log("Local cleanup completed.")
        else:
            self.log("Local test data remains for inspection.")
        
        return True


def main():
    """Main function to run the upload."""
    parser = argparse.ArgumentParser(description='Upload test data to server')
    parser.add_argument('--server', required=True, help='Server URL (e.g., http://your-server.com)')
    parser.add_argument('--user', default='test130', help='User ID for test data (default: test130)')
    parser.add_argument('--cleanup', action='store_true', help='Automatically cleanup local files after upload')
    
    args = parser.parse_args()
    
    print("Test Data Upload Script")
    print("=" * 40)
    print(f"Server: {args.server}")
    print(f"User ID: {args.user}")
    print()
    
    # Check if test file exists
    test_file = Path("test_file.zip")
    if not test_file.exists():
        print(f"❌ Error: test_file.zip not found in current directory")
        print("Please place test_file.zip in the same directory as this script.")
        return False
    
    # Create and run uploader
    uploader = TestDataUploader(args.server, args.user)
    success = uploader.run_upload()
    
    if args.cleanup and success:
        uploader.cleanup_local_files()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
