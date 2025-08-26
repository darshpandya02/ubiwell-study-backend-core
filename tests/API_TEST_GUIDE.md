# API Endpoints Test Script Guide

## Overview
This script tests all endpoints of the Study Framework API to ensure they're working correctly.

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r test_requirements.txt
   ```

2. **Run the Test Script:**
   ```bash
   python test_api_endpoints.py
   ```

## What the Script Tests

### 🔍 Basic Endpoints
- **GET** `/api/v1/health` - Health check
- **GET** `/api/v1/` - Default API endpoint

### 🔐 Authentication Endpoints
- **POST** `/api/v1/credentials/check` - User login verification
- **POST** `/api/v1/credentials/checkCode` - Login code verification

### 👤 User Management Endpoints
- **POST** `/api/v1/user/info/update` - Update user information
- **POST** `/api/v1/user/status/ping` - Phone status ping

### 📁 File Upload Endpoints
- **POST** `/api/v1/data/upload` - General file upload
- **POST** `/api/v1/data/uploadLog` - Log file upload (using format from SensorManagerLogs.txt)
- **POST** `/api/v1/data/daily-diary` - Daily diary upload
- **POST** `/api/v1/data/ema-response` - EMA response upload

### 📊 Other Endpoints
- **POST** `/api/v1/data/ema-request` - Request EMA file
- **POST** `/api/v1/upload-news/` - JSON data upload

### 🔒 Security Tests
- Invalid auth key testing
- Missing auth key testing

## Input Required

When you run the script, it will ask for:

1. **API Base URL** (e.g., `https://bean-study.europa.khoury.northeastern.edu`)
2. **Auth Key** (from your configuration)
3. **Test User ID** (optional, defaults to "testuser")

## Expected Results

### ✅ Successful Responses
- **200** - Operation successful
- **401** - Invalid credentials (expected for auth tests)
- **404** - Resource not found (expected for some tests)

### ❌ Failed Responses
- **403** - Unauthorized (invalid/missing auth key)
- **400** - Bad request
- **500** - Server error
- **0** - Connection/timeout error

## Output

The script provides:
- Real-time test results with emojis and timing
- Detailed error messages for failed tests
- Summary statistics
- JSON file with complete test results

## Example Output

```
🚀 Starting API Endpoints Test Suite
==================================================
Base URL: https://bean-study.europa.khoury.northeastern.edu
Test User: testuser
Timestamp: 2025-08-25 17:30:00
==================================================

📋 Testing Basic Endpoints...
✅ GET /api/v1/health - 200 (0.15s)
✅ GET /api/v1/ - 200 (0.12s)

🔐 Testing Authentication Endpoints...
✅ POST /api/v1/credentials/check - 401 (0.18s)
✅ POST /api/v1/credentials/checkCode - 401 (0.16s)

📁 Testing File Upload Endpoints...
✅ POST /api/v1/data/upload - 200 (0.45s)
✅ POST /api/v1/data/uploadLog - 200 (0.52s)

📊 Test Summary
==================================================
Total Tests: 12
Successful: 12
Failed: 0
Success Rate: 100.0%

📄 Detailed results saved to: api_test_results_20250825_173000.json
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check if the API server is running
   - Verify the base URL is correct
   - Check network connectivity

2. **Auth Key Errors**
   - Verify the auth key matches your configuration
   - Check if the auth key is properly set in the server config

3. **File Upload Errors**
   - Ensure the server has write permissions
   - Check available disk space
   - Verify file type restrictions

4. **Timeout Errors**
   - Increase timeout values in the script if needed
   - Check server performance

### Log Files

The script creates detailed JSON log files with timestamps:
- `api_test_results_YYYYMMDD_HHMMSS.json`

These files contain:
- Complete request/response data
- Timing information
- Error details
- Test summary statistics

## Customization

You can modify the script to:
- Test specific endpoints only
- Use different test data
- Adjust timeout values
- Add custom validation logic
- Test with different user accounts

## Security Notes

- The script uses test data only
- No real user credentials are stored
- All test files are temporary
- Results are saved locally only
