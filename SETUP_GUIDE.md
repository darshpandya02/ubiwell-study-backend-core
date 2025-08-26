# Study Framework Core - Complete Setup Guide

This guide covers everything you need to set up and use the Study Framework Core for your data collection studies using the **Git submodule** approach.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Complete Setup](#complete-setup)
3. [Customization](#customization)
4. [Updates](#updates)
5. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### **For Study Projects (Submodule Setup)**
```bash
# In your study project directory
git submodule add https://github.com/UbiWell/ubiwell-study-backend-core.git
git submodule update --init --recursive

# Run setup script
cd ubiwell-study-backend-core
sudo python setup_study.py "My Study" \
    --user myuser \
    --db-username mydbuser \
    --db-password mydbpass \
    --db-name my_study_db \
    --auth-key my-auth-key \
    --announcement-key my-announcement-key
```

### **For Framework Development**
```bash
# Clone framework for development
git clone https://github.com/UbiWell/ubiwell-study-backend-core.git
cd ubiwell-study-backend-core

# Install in development mode
pip install -e .
```

## 📦 Complete Setup

### Prerequisites
- Ubuntu/Debian server
- Root access (sudo)
- MongoDB installed and running
- **Note**: Anaconda will be installed automatically if not present

### Workflow Overview
The setup process follows this workflow:
1. **Create study project** and initialize Git repository
2. **Add framework as submodule** to your study project
3. **Run setup script** which creates the complete study infrastructure
4. **Install Anaconda** automatically if needed
5. **Setup systemd services** and Nginx configuration
6. **Configure and start** all services

### Step 1: Create Study Project
```bash
# Create your study project directory
mkdir my-study
cd my-study

# Initialize Git repository
git init

# Add framework as submodule
git submodule add https://github.com/UbiWell/ubiwell-study-backend-core.git
git submodule update --init --recursive

# Commit the submodule addition
git add .
git commit -m "Add Study Framework Core as submodule"
```

### Step 2: Run Setup Script
```bash
# Navigate to the framework directory
cd ubiwell-study-backend-core

# Run setup (as root) - Anaconda will be installed automatically if needed
sudo python setup_study.py "My Study" \
    --user myuser \
    --db-username mydbuser \
    --db-password mydbpass \
    --db-host localhost \
    --db-port 27017 \
    --db-name my_study_db \
    --auth-key my-auth-key \
    --announcement-key my-announcement-key
```

**Setup Script Options:**
- `--user myuser` - System user for the study
- `--db-username mydbuser` - MongoDB username
- `--db-password mydbpass` - MongoDB password
- `--db-name my_study_db` - MongoDB database name
- `--auth-key my-auth-key` - API authentication key
- `--announcement-key my-announcement-key` - Announcement system key

**Note**: The setup script automatically:
- Detects and installs Anaconda if needed
- Creates conda environment for your study
- Sets up all systemd services
- Configures Nginx
- Creates admin user for internal web access

### Step 3: Configure Study
Edit the generated config file:
```bash
nano /mnt/study/my-study/config/study_config.json
```

### Step 4: Start Services
```bash
# Start API service (Priority #1 - Data Collection)
sudo systemctl start my-study-api

# Start internal web service (Priority #2 - Dashboard)
sudo systemctl start my-study-internal

# Check status
sudo systemctl status my-study-api my-study-internal

# Enable services to start on boot
sudo systemctl enable my-study-api my-study-internal
```

### Step 5: Setup Cron Jobs
```bash
# Setup automated data processing
sudo /mnt/study/my-study/scripts/setup_cron_jobs.sh --user myuser --env my-study-env
```

### Step 6: Access Your Study
- **API Endpoints**: `https://your-server.com/api/v1/`
- **Internal Dashboard**: `https://your-server.com/internal_web/`
- **Admin Login**: Username: `admin`, Password: (generated during setup)

## 🎨 Customization

### Adding Custom Dashboard Columns

Create your custom dashboard implementation in your study project:

```python
# my_study_implementation/dashboard.py
from study_framework_core import DashboardBase

class MyStudyDashboard(DashboardBase):
    def get_custom_columns(self):
        return [
            "Custom Column 1",
            "Custom Column 2"
        ]
    
    def generate_custom_row_data(self, user_data, daily_summary):
        return {
            "custom_data_1": self._get_custom_data_1(user_data),
            "custom_data_2": self._get_custom_data_2(user_data)
        }
```

### Adding Custom API Endpoints

```python
# my_study_implementation/api.py
from study_framework_core import APIBase
from flask_restful import Resource

class CustomEndpoint(Resource):
    def get(self):
        return {"message": "Custom endpoint"}

class MyStudyAPI(APIBase):
    def get_custom_endpoints(self):
        return [CustomEndpoint]
```

### Adding Custom Data Processing

```python
# my_study_implementation/processing.py
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

### Using Custom Implementations

Update your WSGI files to use custom implementations:

```python
# api_wsgi.py (customized)
from my_study_implementation.api import MyStudyAPI
api_app = MyStudyAPI()
application = api_app

# internal_wsgi.py (customized)
from study_framework_core import InternalWebBase
from my_study_implementation.dashboard import MyStudyDashboard

internal_app = InternalWebBase(dashboard_class=MyStudyDashboard)
application = internal_app
```

## 🔄 Updates

### Updating Core Framework
```bash
# Navigate to your study project
cd /path/to/my-study

# Update the submodule to latest version
cd ubiwell-study-backend-core
git submodule update --remote

# Update the framework
python update_core.py --study-name "My Study"

# Restart services
sudo systemctl restart my-study-api my-study-internal

# Commit the update
cd ..
git add ubiwell-study-backend-core
git commit -m "Update framework to latest version"
```

### What Gets Updated
- ✅ Core framework functionality
- ✅ Bug fixes and improvements
- ✅ Security updates
- ❌ Your custom code (stays intact)
- ❌ Your study configuration (stays intact)

## 🛠️ Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
sudo journalctl -u my-study-api -f
sudo journalctl -u my-study-internal -f

# Check permissions
sudo chown -R myuser:myuser /mnt/study/my-study/

# Fix WSGI files if needed
cd /mnt/study/my-study
python ubiwell-study-backend-core/tests/fix_wsgi_files.py
```

#### 2. Database Connection Failed
```bash
# Check MongoDB status
sudo systemctl status mongod

# Test connection
cd /mnt/study/my-study
conda activate my-study-env
python -c "from study_framework_core.core.handlers import get_db; print(get_db())"
```

#### 3. Nginx Issues
```bash
# Check Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

#### 4. Conda Environment Issues
```bash
# Activate environment
conda activate my-study-env

# Reinstall packages
cd /mnt/study/my-study
python ubiwell-study-backend-core/tests/install_requirements.py
```

#### 5. Admin User Issues
```bash
# Create admin user manually
cd /mnt/study/my-study
python ubiwell-study-backend-core/tests/create_admin_user.py
```

### Health Checks
```bash
# API health
curl https://your-server.com/api/v1/health

# Internal web health
curl https://your-server.com/internal_web/health
```

## 📁 Directory Structure

After setup, your study directory will look like:

```
/mnt/study/my-study/
├── ubiwell-study-backend-core/    # Framework submodule
│   ├── study_framework_core/      # Core framework package
│   ├── docs/                      # Documentation
│   ├── tests/                     # Testing utilities
│   ├── setup_study.py             # Setup script
│   └── update_core.py             # Update script
├── my_study_implementation/       # Your custom code (optional)
├── templates/                     # Custom templates (optional)
├── static/                        # Custom static files (optional)
├── scripts/                       # Processing scripts
├── logs/                          # Application logs
├── data/                          # Data directories
├── config/                        # Configuration files
│   └── study_config.json          # Main configuration
├── api_wsgi.py                    # API WSGI
├── internal_wsgi.py               # Internal WSGI
└── README.md                      # Study-specific docs
```

## 🔧 Configuration Options

### Database Configuration
```json
{
  "database": {
    "host": "localhost",
    "port": 27017,
    "username": "myuser",
    "password": "mypass",
    "database": "my_study_db"
  }
}
```

### Path Configuration
```json
{
  "paths": {
    "data_upload_path": "/mnt/study/my-study/data_uploads/uploads",
    "data_processed_path": "/mnt/study/my-study/data_uploads/processed",
    "ema_file_path": "/mnt/study/my-study/ema_surveys"
  }
}
```

### Security Configuration
```json
{
  "security": {
    "auth_key": "my-auth-key",
    "announcement_pass_key": "my-announcement-key"
  }
}
```

## 🧪 Testing

### API Testing
```bash
# Test all API endpoints
cd /mnt/study/my-study
python ubiwell-study-backend-core/tests/test_api_endpoints.py --server https://your-server.com
```

### Data Pipeline Testing
```bash
# Upload test data
python ubiwell-study-backend-core/tests/upload_test_data.py --server https://your-server.com --user test130

# Process test data
python ubiwell-study-backend-core/tests/test_pipeline_step_by_step.py
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in `/mnt/study/my-study/logs/`
3. Check service status with `systemctl status`
4. Use the testing utilities in `ubiwell-study-backend-core/tests/`
5. Contact the framework maintainers

## 🎯 Next Steps

After setup:
1. **Test the API**: Upload some test data
2. **Check the Dashboard**: Verify data appears correctly
3. **Setup Monitoring**: Monitor logs and service status
4. **Customize**: Add your study-specific features
5. **Deploy**: Make your study available to participants

---

**Need help?** Check the troubleshooting section or contact the framework maintainers.
