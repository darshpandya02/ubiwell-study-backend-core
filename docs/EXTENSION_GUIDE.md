# Extension Guide

This guide explains how to extend the Study Framework Core for your specific study needs.

## 🎨 Extending the Framework

### **Adding Custom Dashboard Columns**

1. **Extend DashboardBase:**
```python
from study_framework_core import DashboardBase

class MyStudyDashboard(DashboardBase):
    def get_custom_columns(self):
        return ["EMA Responses", "App Events"]
    
    def generate_custom_row_data(self, user_data, daily_summary):
        return {
            "ema_responses": self._get_ema_count(user_data),
            "app_events": self._get_app_event_count(user_data)
        }
```

2. **Use in your WSGI file:**
```python
# wsgi_internal.py
from study_framework_core import InternalWebBase
from my_study_implementation.dashboard import MyStudyDashboard

internal_app = InternalWebBase(dashboard_class=MyStudyDashboard)
application = internal_app
```

### **Adding Custom API Endpoints**

1. **Create custom endpoints:**
```python
from flask_restful import Resource

class CustomDataEndpoint(Resource):
    def get(self):
        return {"custom_data": "value"}
    
    def post(self):
        # Handle custom data upload
        pass
```

2. **Extend APIBase:**
```python
from study_framework_core import APIBase

class MyStudyAPI(APIBase):
    def get_custom_endpoints(self):
        return [CustomDataEndpoint]
```

3. **Use in your WSGI file:**
```python
# wsgi_api.py
from my_study_implementation.api import MyStudyAPI
api_app = MyStudyAPI()
application = api_app
```

### **Adding Custom Data Processing**

1. **Extend DataProcessor:**
```python
from study_framework_core.core.processing_scripts import DataProcessor

class MyStudyDataProcessor(DataProcessor):
    def process_phone_data(self, user_id):
        # Call core processing
        super().process_phone_data(user_id)
        
        # Add custom processing
        self._process_custom_data(user_id)
    
    def _process_custom_data(self, user_id):
        # Process study-specific data
        pass
```

2. **Use in your processing scripts:**
```python
# my_study_processing.py
from my_study_implementation.processing import MyStudyDataProcessor

processor = MyStudyDataProcessor()
processor.process_phone_data("user123")
```

## 🔧 Core Classes

### **DashboardBase** (`core/dashboard.py`)
Base class for extensible dashboards.

```python
from study_framework_core import DashboardBase

class MyStudyDashboard(DashboardBase):
    def get_custom_columns(self):
        """Return list of custom column names."""
        return ["Custom Column 1", "Custom Column 2"]
    
    def generate_custom_row_data(self, user_data, daily_summary):
        """Generate data for custom columns."""
        return {
            "custom_data_1": self._get_custom_data_1(user_data),
            "custom_data_2": self._get_custom_data_2(user_data)
        }
```

### **APIBase** (`core/api.py`)
Base class for extensible APIs.

```python
from study_framework_core import APIBase
from flask_restful import Resource

class CustomEndpoint(Resource):
    def get(self):
        return {"message": "Custom endpoint"}

class MyStudyAPI(APIBase):
    def get_custom_endpoints(self):
        """Return list of custom endpoint classes."""
        return [CustomEndpoint]
```

### **DataProcessor** (`core/processing_scripts.py`)
Base class for data processing.

```python
from study_framework_core.core.processing_scripts import DataProcessor

class MyStudyDataProcessor(DataProcessor):
    def process_phone_data(self, user_id):
        # Call core processing
        super().process_phone_data(user_id)
        
        # Add custom processing
        self._process_custom_data(user_id)
    
    def _process_custom_data(self, user_id):
        # Your custom processing logic
        pass
```

## ⚙️ Configuration

### **Configuration Structure**
```python
from study_framework_core.core.config import get_config

config = get_config()

# Access different sections
db_config = config.database
server_config = config.server
security_config = config.security
paths_config = config.paths
```

### **Configuration File Format**
```json
{
  "study_name": "My Study",
  "database": {
    "host": "localhost",
    "port": 27017,
    "username": "myuser",
    "password": "mypass",
    "database": "my_study_db"
  },
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "socket_path": "/var/sockets/my-study.sock"
  },
  "security": {
    "auth_key": "my-auth-key",
    "announcement_pass_key": "my-announcement-key"
  },
  "paths": {
    "data_upload_path": "/mnt/study/my-study/data/uploads",
    "data_processed_path": "/mnt/study/my-study/data/processed",
    "ema_file_path": "/mnt/study/my-study/ema_surveys"
  }
}
```

## 🔄 Update Process

### **For Framework Maintainers:**
1. **Make changes** to core classes
2. **Update version** in `pyproject.toml`
3. **Push to repository**
4. **Users update** with `python update_core.py --study-name "My Study"`

### **For Study Developers:**
1. **Extend core classes** in your own files
2. **Keep custom code separate** from core
3. **Update core independently** when needed
4. **Test customizations** after core updates

## 🧪 Testing

### **Testing Custom Extensions**
```python
# test_my_study_dashboard.py
import unittest
from my_study_implementation.dashboard import MyStudyDashboard

class TestMyStudyDashboard(unittest.TestCase):
    def setUp(self):
        self.dashboard = MyStudyDashboard()
    
    def test_custom_columns(self):
        columns = self.dashboard.get_custom_columns()
        self.assertIn("EMA Responses", columns)
        self.assertIn("App Events", columns)
```

### **Testing Custom API Endpoints**
```python
# test_my_study_api.py
import unittest
from my_study_implementation.api import MyStudyAPI

class TestMyStudyAPI(unittest.TestCase):
    def setUp(self):
        self.api = MyStudyAPI()
    
    def test_custom_endpoints(self):
        endpoints = self.api.get_custom_endpoints()
        self.assertTrue(len(endpoints) > 0)
```

## 🐛 Debugging

### **Common Issues**

1. **Import Errors:**
```python
# Make sure you're importing from the right place
from study_framework_core import DashboardBase  # ✅
from study_framework_core.core.dashboard import DashboardBase  # ✅
```

2. **Configuration Issues:**
```python
# Check if config file exists and is valid
config = get_config()
print(config.database.host)  # Should print database host
```

3. **Database Connection:**
```python
# Test database connection
from study_framework_core.core.handlers import get_db
db = get_db()
print(db.list_collection_names())  # Should print collections
```

## 📦 Package Structure

```
study_framework_core/
├── __init__.py                 # Package exports
├── core/                       # Core framework classes
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── dashboard.py           # Dashboard base classes
│   ├── api.py                 # API base classes
│   ├── processing.py          # Data processing base classes
│   ├── internal_web.py        # Internal web interface
│   ├── handlers.py            # Common helper functions
│   ├── schemas.py             # API request schemas
│   └── processing_scripts.py  # Backend processing logic
├── templates/                  # Core HTML templates
│   ├── dashboard_base.html
│   ├── navigation.html
│   ├── login.html
│   ├── landing_page.html
│   └── user_management.html
├── static/                     # Core static files
│   ├── css/
│   │   └── core_styles.css
│   └── js/
│       └── core_dashboard.js
└── scripts/                    # Processing scripts
    ├── process_data.sh
    ├── generate_summaries.sh
    └── setup_cron_jobs.sh
```

---

**For setup instructions, see [SETUP_GUIDE.md](../SETUP_GUIDE.md).**
**For API reference, see [API_REFERENCE.md](API_REFERENCE.md).**
