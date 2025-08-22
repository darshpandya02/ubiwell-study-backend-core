#!/usr/bin/env python3
"""
Upload Test Data Script

This script uploads test data from a local machine to the server.
The user must already exist on the server (created via test_pipeline_step_by_step.py).
Run this from your local machine to upload the test data.

Usage:
    python upload_test_data.py --server http://your-server.com --user test130 --token YOUR_AUTH_TOKEN
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
    
    def __init__(self, server_url: str, user_id: str, auth_token: str):
        self.server_url = server_url.rstrip('/')
        self.user_id = user_id
        self.auth_token = auth_token
        self.test_data_dir = Path("test_data")
        
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
    

    
    def upload_file(self, file_path: Path) -> bool:
        """Upload a single file to the server."""
        try:
            url = f"{self.server_url}/api/v1/data/upload"
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                data = {
                    'uid': self.user_id,
                    'auth_key': self.auth_token
                }
                
                response = requests.post(url, files=files, data=data, timeout=60)
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        self.log(f"Response: {result}")  # Debug: show actual response
                        
                        # Check for different possible success indicators
                        if (result.get('info') == 'upload successful' or 
                            result.get('status') == 'success' or
                            result.get('message') == 'upload successful' or
                            (result.get('message') and result['message'].get('info') == 'upload successful')):
                            self.log(f"✅ Uploaded: {file_path.name}")
                            return True
                        else:
                            self.log(f"❌ Upload failed: {result}")
                            return False
                    except Exception as e:
                        self.log(f"❌ Error parsing response: {e}")
                        self.log(f"Raw response: {response.text}")
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
        self.log(f"Data uploaded for user {self.user_id}.")
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
    parser.add_argument('--user', default='test130', help='User ID for test data (must already exist on server, default: test130)')
    parser.add_argument('--token', required=True, help='Authentication token for the user')
    parser.add_argument('--cleanup', action='store_true', help='Automatically cleanup local files after upload')
    
    args = parser.parse_args()
    
    print("Test Data Upload Script")
    print("=" * 40)
    print(f"Server: {args.server}")
    print(f"User ID: {args.user}")
    print(f"Auth Token: {args.token[:10]}..." if len(args.token) > 10 else f"Auth Token: {args.token}")
    print()
    
    # Check if test file exists
    test_file = Path("test_file.zip")
    if not test_file.exists():
        print(f"❌ Error: test_file.zip not found in current directory")
        print("Please place test_file.zip in the same directory as this script.")
        print("\nWorkflow:")
        print("1. First run test_pipeline_step_by_step.py on the server to create the user")
        print("2. Then run this script from your local machine to upload data")
        return False
    
    # Create and run uploader
    uploader = TestDataUploader(args.server, args.user, args.token)
    success = uploader.run_upload()
    
    if args.cleanup and success:
        uploader.cleanup_local_files()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
