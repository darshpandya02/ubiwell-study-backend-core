#!/usr/bin/env python3
"""
API Endpoints Test Script
Tests all endpoints of the Study Framework API
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

class APITester:
    def __init__(self, base_url: str, auth_key: str):
        self.base_url = base_url.rstrip('/')
        self.auth_key = auth_key
        self.session = requests.Session()
        self.results = []
        
    def log_test(self, endpoint: str, method: str, status_code: int, response_time: float, 
                 success: bool, error: Optional[str] = None, details: Optional[Dict] = None):
        """Log test results"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time': response_time,
            'success': success,
            'error': error,
            'details': details
        }
        self.results.append(result)
        
        # Print result
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {method} {endpoint} - {status_code} ({response_time:.2f}s)")
        if error:
            print(f"   Error: {error}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_health_check(self):
        """Test health check endpoint"""
        endpoint = f"{self.base_url}/api/v1/health"
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/health", "GET", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/health", "GET", 0, response_time, False, str(e))

    def test_default_endpoint(self):
        """Test default API endpoint"""
        endpoint = f"{self.base_url}/api/v1/"
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/", "GET", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/", "GET", 0, response_time, False, str(e))

    def test_login_endpoint(self, uid: str = "testuser", password: str = "testpass", device: str = "ios"):
        """Test login endpoint"""
        endpoint = f"{self.base_url}/api/v1/credentials/check"
        start_time = time.time()
        
        payload = {
            "uid": uid,
            "password": password,
            "device": device,
            "auth_key": self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 401]  # 401 is expected for invalid credentials
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/credentials/check", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/credentials/check", "POST", 0, response_time, False, str(e))

    def test_login_code_endpoint(self, uid: str = "testuser", code: str = "", device: str = "ios"):
        """Test login code endpoint"""
        endpoint = f"{self.base_url}/api/v1/credentials/checkCode"
        start_time = time.time()
        
        payload = {
            "uid": uid,
            "code": code,
            "device": device,
            "auth_key": self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 401]  # 401 is expected for invalid code
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/credentials/checkCode", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/credentials/checkCode", "POST", 0, response_time, False, str(e))

    def test_user_info_endpoint(self, uid: str = "testuser"):
        """Test user info update endpoint"""
        endpoint = f"{self.base_url}/api/v1/user/info/update"
        start_time = time.time()
        
        payload = {
            "uid": uid,
            "info_key": "test_key",
            "info_value": "test_value",
            "auth_key": self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/user/info/update", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/user/info/update", "POST", 0, response_time, False, str(e))

    def test_phone_ping_endpoint(self, uid: str = "testuser"):
        """Test phone ping endpoint"""
        endpoint = f"{self.base_url}/api/v1/user/status/ping"
        start_time = time.time()
        
        payload = {
            "uid": uid,
            "device": "ios",
            "device_type": "iPhone",
            "auth_key": self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/user/status/ping", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/user/status/ping", "POST", 0, response_time, False, str(e))

    def test_upload_file_endpoint(self, uid: str = "testuser"):
        """Test file upload endpoint"""
        endpoint = f"{self.base_url}/api/v1/data/upload"
        start_time = time.time()
        
        # Create a test file
        test_file_content = "This is a test file for API testing"
        test_filename = "test_file.txt"
        
        files = {'file': (test_filename, test_file_content, 'text/plain')}
        data = {
            'uid': uid,
            'auth_key': self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, files=files, data=data, timeout=30)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/data/upload", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/data/upload", "POST", 0, response_time, False, str(e))

    def test_upload_logfile_endpoint(self, uid: str = "testuser"):
        """Test log file upload endpoint"""
        endpoint = f"{self.base_url}/api/v1/data/uploadLog"
        start_time = time.time()
        
        # Create a test log file based on the example
        test_log_content = """15.08.25 17:17:37 heartbeat2
15.08.25 17:17:37 Log file deleted after 7 days
15.08.25 17:17:37 EMA fetched and saved in local storage
15.08.25 17:17:37 auto loading configs
15.08.25 17:17:37 Auto reload config time difference is not 6 hrs yet
15.08.25 17:17:37 heartbeat2
15.08.25 17:17:37 Starting Garmin device sync
15.08.25 17:17:37 Garmin connected: true
15.08.25 17:17:37 Garmin firmware: 3.22
15.08.25 17:17:37 App version: 2.11"""
        
        test_filename = "test_log.txt"
        
        files = {'file': (test_filename, test_log_content, 'text/plain')}
        data = {
            'uid': uid,
            'auth_key': self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, files=files, data=data, timeout=30)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/data/uploadLog", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/data/uploadLog", "POST", 0, response_time, False, str(e))

    def test_upload_daily_diary_endpoint(self, uid: str = "testuser"):
        """Test daily diary upload endpoint"""
        endpoint = f"{self.base_url}/api/v1/data/daily-diary"
        start_time = time.time()
        
        # Create a test daily diary file
        test_diary_content = """{
  "date": "2025-08-25",
  "mood": "good",
  "sleep_hours": 8,
  "stress_level": 3,
  "notes": "Test diary entry"
}"""
        
        test_filename = "daily_diary.json"
        
        files = {'file': (test_filename, test_diary_content, 'application/json')}
        data = {
            'uid': uid,
            'auth_key': self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, files=files, data=data, timeout=30)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/data/daily-diary", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/data/daily-diary", "POST", 0, response_time, False, str(e))

    def test_upload_ema_endpoint(self, uid: str = "testuser"):
        """Test EMA upload endpoint"""
        endpoint = f"{self.base_url}/api/v1/data/ema-response"
        start_time = time.time()
        
        # Create a test EMA response file
        test_ema_content = """{
  "timestamp": "2025-08-25T17:30:00Z",
  "question_id": "mood_001",
  "response": "5",
  "response_time": 2.5
}"""
        
        test_filename = "ema_response.json"
        
        files = {'file': (test_filename, test_ema_content, 'application/json')}
        data = {
            'uid': uid,
            'auth_key': self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, files=files, data=data, timeout=30)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/data/ema-response", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/data/ema-response", "POST", 0, response_time, False, str(e))

    def test_request_ema_file_endpoint(self, uid: str = "testuser"):
        """Test EMA file request endpoint"""
        endpoint = f"{self.base_url}/api/v1/data/ema-request"
        start_time = time.time()
        
        payload = {
            "uid": uid,
            "auth_key": self.auth_key
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 404]  # 404 if no EMA file exists
            details = {
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content) if response.content else 0
            }
            
            self.log_test("/api/v1/data/ema-request", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/data/ema-request", "POST", 0, response_time, False, str(e))

    def test_upload_json_endpoint(self, uid: str = "testuser"):
        """Test JSON upload endpoint"""
        endpoint = f"{self.base_url}/api/v1/upload-news/"
        start_time = time.time()
        
        payload = {
            "uid": uid,
            "data": {
                "news_id": "test_001",
                "title": "Test News Article",
                "content": "This is a test news article for API testing",
                "timestamp": "2025-08-25T17:30:00Z"
            },
            "data_type": "news_task"
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
            self.log_test("/api/v1/upload-news/", "POST", response.status_code, response_time, success, 
                         details=details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/api/v1/upload-news/", "POST", 0, response_time, False, str(e))

    def test_invalid_auth_key(self):
        """Test endpoints with invalid auth key"""
        print("🔒 Testing with invalid auth key...")
        
        # Test login with invalid auth key
        endpoint = f"{self.base_url}/api/v1/credentials/check"
        payload = {
            "uid": "testuser",
            "password": "testpass",
            "device": "ios",
            "auth_key": "invalid_key"
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            success = response.status_code == 403
            print(f"{'✅' if success else '❌'} Invalid auth key test - {response.status_code}")
        except Exception as e:
            print(f"❌ Invalid auth key test failed: {e}")
        print()

    def test_missing_auth_key(self):
        """Test endpoints without auth key"""
        print("🔒 Testing without auth key...")
        
        # Test login without auth key
        endpoint = f"{self.base_url}/api/v1/credentials/check"
        payload = {
            "uid": "testuser",
            "password": "testpass",
            "device": "ios"
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            success = response.status_code == 403
            print(f"{'✅' if success else '❌'} Missing auth key test - {response.status_code}")
        except Exception as e:
            print(f"❌ Missing auth key test failed: {e}")
        print()

    def run_all_tests(self, test_uid: str = "testuser"):
        """Run all API tests"""
        print("🚀 Starting API Endpoints Test Suite")
        print("=" * 50)
        print(f"Base URL: {self.base_url}")
        print(f"Test User: {test_uid}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print()

        # Test basic endpoints
        print("📋 Testing Basic Endpoints...")
        self.test_health_check()
        self.test_default_endpoint()
        print()

        # Test authentication endpoints
        print("🔐 Testing Authentication Endpoints...")
        self.test_login_endpoint(test_uid)
        self.test_login_code_endpoint(test_uid)
        print()

        # Test user management endpoints
        print("👤 Testing User Management Endpoints...")
        self.test_user_info_endpoint(test_uid)
        self.test_phone_ping_endpoint(test_uid)
        print()

        # Test file upload endpoints
        print("📁 Testing File Upload Endpoints...")
        self.test_upload_file_endpoint(test_uid)
        self.test_upload_logfile_endpoint(test_uid)
        self.test_upload_daily_diary_endpoint(test_uid)
        self.test_upload_ema_endpoint(test_uid)
        print()

        # Test other endpoints
        print("📊 Testing Other Endpoints...")
        self.test_request_ema_file_endpoint(test_uid)
        self.test_upload_json_endpoint(test_uid)
        print()

        # Test security
        print("🔒 Testing Security...")
        self.test_invalid_auth_key()
        self.test_missing_auth_key()
        print()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 Test Summary")
        print("=" * 50)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['method']} {result['endpoint']}: {result['error']}")
            print()
        
        # Save results to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"api_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'test_info': {
                    'base_url': self.base_url,
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (successful_tests/total_tests*100) if total_tests > 0 else 0
                },
                'results': self.results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: {filename}")


def main():
    """Main function"""
    print("🔧 Study Framework API Test Script")
    print("=" * 40)
    
    # Get configuration from user
    base_url = input("Enter API base URL (e.g., https://bean-study.europa.khoury.northeastern.edu): ").strip()
    auth_key = input("Enter auth key: ").strip()
    test_uid = input("Enter test user ID (default: testuser): ").strip() or "testuser"
    
    if not base_url or not auth_key:
        print("❌ Base URL and auth key are required!")
        return
    
    print()
    
    # Create tester and run tests
    tester = APITester(base_url, auth_key)
    tester.run_all_tests(test_uid)


if __name__ == "__main__":
    main()
