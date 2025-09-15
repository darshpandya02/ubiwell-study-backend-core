# Tests Directory

This directory contains testing utilities and scripts for the Study Framework Core.

## 📁 Test Files

### **API Testing**
- `test_api_endpoints.py` - Comprehensive API endpoint testing script
- `API_TEST_GUIDE.md` - Guide for testing API endpoints

### **Data Testing**
- `test-files.zip` - Test data archive for pipeline testing
- `upload_test_data.py` - Script to upload test data from local machine
- `test_pipeline_step_by_step.py` - Interactive testing script for debugging

### **Utility Testing**
- `install_requirements.py` - Script to install requirements in conda environment
- `create_admin_user.py` - Script to create admin user for internal web
- `fix_wsgi_files.py` - Utility to fix WSGI file configurations

## 🧪 Running Tests

### **API Testing**
```bash
# Test all API endpoints
python tests/test_api_endpoints.py --server https://your-domain.com

# Follow the API testing guide
# See tests/API_TEST_GUIDE.md for detailed instructions
```

### **Data Pipeline Testing**
```bash
# Upload test data
python tests/upload_test_data.py --server https://your-domain.com --user test130

# Process test data
python tests/test_pipeline_step_by_step.py
```

### **Utility Testing**
```bash
# Install requirements
python tests/install_requirements.py

# Create admin user
python tests/create_admin_user.py

# Fix WSGI files if needed
python tests/fix_wsgi_files.py
```

## 📋 Test Data

The `test-files.zip` contains sample data files for testing:
- Phone data files
- Garmin FIT files
- Log files
- Sample user data

Extract this file to test the complete data processing pipeline.

## 🔧 Test Environment

Tests should be run in the study's conda environment:
```bash
conda activate your-study-env
cd /path/to/your/study
python tests/test_api_endpoints.py
```

## 📖 Documentation

- **[API Testing Guide](API_TEST_GUIDE.md)** - Complete API testing instructions
- **[Main Documentation](../docs/README.md)** - Framework documentation index


