# Study Framework Core - Complete Setup Guide

This guide covers everything you need to set up and use the Study Framework Core for your data collection studies.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Complete Setup](#complete-setup)
3. [Customization](#customization)
4. [Updates](#updates)
5. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### For Developers (Just the Package)
```bash
pip install git+https://github.com/UbiWell/ubiwell-study-backend-core.git
```

### For Complete Study Setup
```bash
git clone https://github.com/UbiWell/ubiwell-study-backend-core.git
cd ubiwell-study-backend-core
python setup_study.py "My Study" --user myuser
```

## 📦 Complete Setup

### Prerequisites
- Ubuntu/Debian server
- Root access (sudo)
- MongoDB installed and running
- **Note**: Anaconda will be installed automatically at `{base-dir}/anaconda3` if not present

### Workflow Overview
The setup process follows this workflow:
1. **Clone framework temporarily** to `/tmp/study-framework`
2. **Run setup script** which creates study at `{base-dir}/{study-name}/`
3. **Install Anaconda** at `{base-dir}/anaconda3/` if needed
4. **Create conda environment** for the study
5. **Setup systemd services** and Nginx configuration
6. **Clean up** temporary framework files

### Step 1: Clone and Setup
```bash
# Clone the framework temporarily
git clone https://github.com/UbiWell/ubiwell-study-backend-core.git /tmp/study-framework
cd /tmp/study-framework

# Run setup (as root) - Anaconda will be installed automatically if needed
sudo python setup_study.py "My Study" \
    --user myuser \
    --base-dir /mnt/study \
    --db-username mydbuser \
    --db-password mydbpass \
    --db-host localhost \
    --db-port 27017 \
    --db-name my_study_db \
    --auth-key my-auth-key \
    --announcement-key my-announcement-key

# Clean up framework files (optional)
rm -rf /tmp/study-framework
```

**Base Directory Options:**
- `--base-dir /mnt/study` (default) - Standard location
- `--base-dir /opt/studies` - Alternative location
- `--base-dir /home/myuser/studies` - User-specific location

**Note**: The framework is cloned temporarily and cleaned up after setup. The study data and Anaconda installation remain in the specified base directory. The framework package is installed from the `study_framework_core/` subdirectory.

### Step 2: Configure
Edit the generated config file:
```bash
nano /mnt/study/my-study/study_config.json
```

**Note**: If Anaconda was installed automatically, it will be located at `{base-dir}/anaconda3/`. The setup script automatically:
- Downloads and installs Anaconda 2023.09
- Adds it to the system PATH via `/etc/profile.d/conda.sh`
- Creates conda environments for your studies

### Step 3: Start Services
```bash
# Start API service (Priority #1 - Data Collection)
sudo systemctl start my-study-api

# Start internal web service (Priority #2 - Dashboard)
sudo systemctl start my-study-internal

# Check status
sudo systemctl status my-study-api my-study-internal
```

### Step 4: Setup Cron Jobs
```bash
# Setup automated data processing
sudo /mnt/study/my-study/scripts/setup_cron_jobs.sh --user myuser --env my-study-env
```

### Step 5: Access Your Study
- **API Endpoints**: `http://your-server.com/api/v1/`
- **Internal Dashboard**: `http://your-server.com/internal_web/`
- **Admin Login**: Username: `admin`, Password: (generated during setup)

## 🎨 Customization

### Adding Custom Dashboard Columns

Create your custom dashboard implementation:

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

Update your WSGI files:

```python
# wsgi_api.py
from my_study_implementation.api import MyStudyAPI
api_app = MyStudyAPI()
application = api_app

# wsgi_internal.py
from study_framework_core import InternalWebBase
from my_study_implementation.dashboard import MyStudyDashboard

internal_app = InternalWebBase(dashboard_class=MyStudyDashboard)
application = internal_app
```

## 🔄 Updates

### Updating Core Framework
```bash
# Option 1: Using update script
python update_core.py --study-name "My Study"

# Option 2: Using setup script
python setup_study.py "My Study" --update

# Option 3: Manual update
git pull origin main
conda run -n my-study-env pip install --upgrade -e .
sudo systemctl restart my-study-api my-study-internal
```

### What Gets Updated
- ✅ Core framework functionality
- ✅ Bug fixes and improvements
- ✅ Security updates
- ❌ Your custom code (stays intact)

## 🛠️ Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
sudo journalctl -u my-study-api -f
sudo journalctl -u my-study-internal -f

# Check permissions
sudo chown -R myuser:myuser /mnt/study/my-study/
```

#### 2. Database Connection Failed
```bash
# Check MongoDB status
sudo systemctl status mongod

# Test connection
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
pip install -r requirements.txt
```

### Health Checks
```bash
# API health
curl http://your-server.com/api/health

# Internal web health
curl http://your-server.com/internal/health
```

## 📁 Directory Structure

After setup, your study directory will look like:

```
/mnt/study/my-study/
├── study_framework_core/          # Core framework
├── my_study_implementation/       # Your custom code (optional)
├── templates/                     # Custom templates (optional)
├── static/                        # Custom static files (optional)
├── scripts/                       # Processing scripts
├── logs/                          # Application logs
├── data/                          # Data directories
├── study_config.json              # Configuration
├── wsgi_api.py                    # API WSGI
├── wsgi_internal.py               # Internal WSGI
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
    "data_upload_path": "/mnt/study/my-study/data/uploads",
    "data_processed_path": "/mnt/study/my-study/data/processed",
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

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in `/mnt/study/my-study/logs/`
3. Check service status with `systemctl status`
4. Contact the framework maintainers

## 🎯 Next Steps

After setup:
1. **Test the API**: Upload some test data
2. **Check the Dashboard**: Verify data appears correctly
3. **Setup Monitoring**: Monitor logs and service status
4. **Customize**: Add your study-specific features
5. **Deploy**: Make your study available to participants

---

**Need help?** Check the troubleshooting section or contact the framework maintainers.
