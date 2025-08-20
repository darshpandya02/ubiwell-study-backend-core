# Study Framework Core

A modular, reusable framework for data collection studies that provides core functionality while allowing easy customization for individual studies.

## 🚀 Quick Start

### For Developers (Just the Package)
```bash
pip install git+https://github.com/your-org/study-framework-core.git
```

### For Complete Study Setup
```bash
git clone https://github.com/your-org/study-framework-core.git
cd study-framework-core
python setup_study.py "My Study" --user myuser
```

## 📋 What This Framework Provides

### ✅ **Core Features**
- **API Endpoints**: User authentication, file uploads, data collection
- **Internal Dashboard**: Data monitoring, participant management
- **Data Processing**: Phone data, Garmin FIT files, daily summaries
- **User Management**: Participant creation, credential generation
- **Automated Processing**: Cron jobs for data processing and summaries

### ✅ **Modular Architecture**
- **Core Framework**: Standard functionality for all studies
- **Study-Specific Extensions**: Custom dashboard columns, API endpoints, processing
- **Easy Updates**: Update core without affecting customizations
- **Private Distribution**: Git-based installation (no PyPI required)

## 🎯 Use Cases

### **New Study Setup**
```bash
# Complete automated setup
python setup_study.py "My Study" \
    --user myuser \
    --db-username mydbuser \
    --db-password mydbpass
```

### **Adding Custom Features**
```python
# Extend core dashboard
class MyStudyDashboard(DashboardBase):
    def get_custom_columns(self):
        return ["Custom Column 1", "Custom Column 2"]
    
    def generate_custom_row_data(self, user_data, daily_summary):
        return {"custom_data": self._get_custom_data(user_data)}
```

### **Updating Core Framework**
```bash
# Get latest improvements
python update_core.py --study-name "My Study"
```

## 📁 Repository Structure

```
study-framework-core/
├── study_framework_core/          # Core package
│   ├── core/                     # Core classes and interfaces
│   ├── templates/                # Core templates
│   ├── static/                   # Core static files
│   └── scripts/                  # Processing scripts
├── setup_study.py                # Automated setup script
├── update_core.py                # Update script
├── requirements.txt              # Dependencies
├── SETUP_GUIDE.md               # Complete setup guide
└── README.md                    # This file
```

## 🔧 Key Components

### **Core Package (`study_framework_core/`)**
- **`core/dashboard.py`**: Extensible dashboard system
- **`core/api.py`**: Standard API endpoints
- **`core/processing.py`**: Data processing pipeline
- **`core/internal_web.py`**: Internal web interface
- **`core/handlers.py`**: Common helper functions

### **Setup Scripts**
- **`setup_study.py`**: Complete study deployment
- **`update_core.py`**: Framework updates

### **Documentation**
- **`SETUP_GUIDE.md`**: Comprehensive setup instructions
- **`study_framework_core/README.md`**: Developer documentation

## 🎨 Customization Examples

### **Connect Study Implementation**
```python
# Custom dashboard with EMA, app events, depression scores
class ConnectStudyDashboard(DashboardBase):
    def get_custom_columns(self):
        return [
            "EMA Responses",
            "App Events", 
            "Daily Diary",
            "Depression Score"
        ]
```

### **Custom API Endpoints**
```python
# Study-specific API endpoints
class MyStudyAPI(APIBase):
    def get_custom_endpoints(self):
        return [CustomEndpoint1, CustomEndpoint2]
```

### **Custom Data Processing**
```python
# Study-specific data processing
class MyStudyDataProcessor(DataProcessor):
    def process_phone_data(self, user_id):
        super().process_phone_data(user_id)  # Core processing
        self._process_custom_data(user_id)   # Custom processing
```

## 🔄 Update Workflow

### **When You Release Updates:**
1. **Push changes** to your repository
2. **Users update** with `python update_core.py --study-name "My Study"`
3. **Core improvements** are applied automatically
4. **Custom code** stays intact

### **When Users Add Custom Features:**
1. **Extend core classes** in their own files
2. **Commit to their repository** (not yours)
3. **Update core independently** when needed

## 📖 Documentation

- **[Complete Setup Guide](SETUP_GUIDE.md)**: Step-by-step setup instructions
- **[Developer Guide](study_framework_core/README.md)**: Framework development and extension
- **[Framework Summary](FRAMEWORK_SUMMARY.md)**: Architecture overview

## 🛠️ Requirements

- **Python**: 3.8+
- **Server**: Ubuntu/Debian with root access
- **Database**: MongoDB
- **Web Server**: Nginx (auto-configured)
- **Process Manager**: Systemd (auto-configured)

## 🚀 Getting Started

1. **Clone the repository**
2. **Follow [SETUP_GUIDE.md](SETUP_GUIDE.md)** for complete setup
3. **Customize** for your study needs
4. **Deploy** and start collecting data!

## 📞 Support

For setup help, see the [troubleshooting section](SETUP_GUIDE.md#troubleshooting) in the setup guide.

---

**Ready to build your data collection study?** Start with the [Complete Setup Guide](SETUP_GUIDE.md)! 🚀

