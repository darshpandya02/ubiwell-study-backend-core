# Ubiwell Study Backend Core - Project Structure

This document outlines the complete structure of the Ubiwell Study Backend Core framework.

## 📁 Complete Directory Structure

```
ubiwell-study-backend-core/
├── 📄 README.md                           # Main project overview and quick start
├── 📄 SETUP_GUIDE.md                      # Complete setup instructions
├── 📄 FRAMEWORK_SUMMARY.md                # Framework architecture overview
├── 📄 PROJECT_STRUCTURE.md                # This file
├── 📄 requirements.txt                    # Python dependencies
├── 📄 setup_study.py                      # Automated study setup script
├── 📄 update_core.py                      # Framework update script
├── 📄 TEST_README.md                      # Testing documentation
├── 📄 test-files.zip                      # Test data for pipeline testing
├── 📄 upload_test_data.py                 # Test data upload script
├── 📄 process_test_data.py                # Test data processing script
├── 📄 test_pipeline_step_by_step.py       # Interactive testing script
│
├── 📦 study_framework_core/               # Core framework package
│   ├── 📄 __init__.py                     # Package exports
│   ├── 📄 pyproject.toml                  # Package configuration
│   ├── 📄 README.md                       # Developer documentation
│   │
│   ├── 🔧 core/                           # Core framework classes
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py                   # Configuration management
│   │   ├── 📄 dashboard.py                # Dashboard base classes
│   │   ├── 📄 api.py                      # API base classes
│   │   ├── 📄 processing.py               # Data processing base classes
│   │   ├── 📄 internal_web.py             # Internal web interface
│   │   ├── 📄 handlers.py                 # Common helper functions
│   │   ├── 📄 schemas.py                  # API request schemas
│   │   └── 📄 processing_scripts.py       # Backend processing logic
│   │
│   ├── 🎨 templates/                      # Core HTML templates
│   │   ├── 📄 dashboard_base.html         # Base dashboard template
│   │   ├── 📄 navigation.html             # Navigation template
│   │   ├── 📄 login.html                  # Login page template
│   │   ├── 📄 landing_page.html           # Landing page template
│   │   └── 📄 user_management.html        # User management template
│   │
│   ├── 🎨 static/                         # Core static files
│   │   ├── 📁 css/
│   │   │   └── 📄 core_styles.css         # Core CSS styles
│   │   └── 📁 js/
│   │       └── 📄 core_dashboard.js       # Core JavaScript
│   │
│   ├── 📜 scripts/                        # Processing scripts
│   │   ├── 📄 process_data.sh             # Data processing script
│   │   ├── 📄 generate_summaries.sh       # Summary generation script
│   │   └── 📄 setup_cron_jobs.sh          # Cron job setup script
│   │
│   └── 📚 examples/                       # Example implementations
│       └── 📄 study_with_config.py        # Example study configuration
```

## 📋 File Descriptions

### **Root Level Files**

| File | Purpose |
|------|---------|
| `README.md` | Main project overview, quick start, and framework features |
| `SETUP_GUIDE.md` | Complete step-by-step setup instructions |
| `FRAMEWORK_SUMMARY.md` | Detailed framework architecture and design |
| `PROJECT_STRUCTURE.md` | This file - complete structure documentation |
| `requirements.txt` | Python package dependencies |
| `setup_study.py` | Automated script for deploying new studies |
| `update_core.py` | Script for updating core framework |
| `TEST_README.md` | Testing documentation and instructions |
| `test-files.zip` | Test data for pipeline verification |
| `upload_test_data.py` | Script to upload test data from local machine |
| `process_test_data.py` | Script to process uploaded test data on server |
| `test_pipeline_step_by_step.py` | Interactive testing script for debugging |

### **Core Package (`study_framework_core/`)**

#### **Core Classes (`core/`)**
| File | Purpose |
|------|---------|
| `config.py` | Configuration management with JSON and environment variables |
| `dashboard.py` | Extensible dashboard system with base classes |
| `api.py` | Standard API endpoints and base classes |
| `processing.py` | Data processing base classes and interfaces |
| `internal_web.py` | Internal web interface with authentication |
| `handlers.py` | Common helper functions for database, files, auth |
| `schemas.py` | Marshmallow schemas for API request validation |
| `processing_scripts.py` | Backend data processing logic and cron jobs |

#### **Templates (`templates/`)**
| File | Purpose |
|------|---------|
| `dashboard_base.html` | Base dashboard template for extension |
| `navigation.html` | Navigation template |
| `login.html` | Admin login page |
| `landing_page.html` | Post-login landing page with module selection |
| `user_management.html` | Participant management interface |

#### **Static Files (`static/`)**
| File | Purpose |
|------|---------|
| `css/core_styles.css` | Core CSS styles for dashboard |
| `js/core_dashboard.js` | Core JavaScript for dashboard interactivity |

#### **Scripts (`scripts/`)**
| File | Purpose |
|------|---------|
| `process_data.sh` | Bash script for data processing |
| `generate_summaries.sh` | Bash script for summary generation |
| `setup_cron_jobs.sh` | Bash script for cron job automation |

## 🎯 Usage Workflow

### **1. Initial Setup**
```bash
# Clone and setup new study
git clone https://github.com/UbiWell/ubiwell-study-backend-core.git
cd ubiwell-study-backend-core
python setup_study.py "My Study" --user myuser
```

### **2. Testing**
```bash
# Upload test data
python upload_test_data.py --server http://your-server.com --user test130

# Process test data
python process_test_data.py --user test130

# Interactive testing
python test_pipeline_step_by_step.py
```

### **3. Updates**
```bash
# Update core framework
python update_core.py --study-name "My Study"
```

## 🔧 Key Components

### **Core Framework Features**
- ✅ **API Endpoints**: User auth, file uploads, data collection
- ✅ **Internal Dashboard**: Data monitoring, participant management
- ✅ **Data Processing**: Phone data, Garmin FIT files, daily summaries
- ✅ **User Management**: Participant creation, credential generation
- ✅ **Automated Processing**: Cron jobs for data processing
- ✅ **Authentication**: Admin login, session management
- ✅ **Configuration**: Centralized JSON configuration

### **Modular Architecture**
- ✅ **Core Framework**: Standard functionality for all studies
- ✅ **Study-Specific Extensions**: Custom dashboard columns, API endpoints
- ✅ **Easy Updates**: Update core without affecting customizations
- ✅ **Private Distribution**: Git-based installation

## 📚 Documentation Hierarchy

```
📖 Documentation Structure
├── README.md                    # 🚀 Main entry point
├── SETUP_GUIDE.md              # 🛠️ Complete setup instructions
├── FRAMEWORK_SUMMARY.md        # 🏗️ Architecture overview
├── PROJECT_STRUCTURE.md        # 📁 This file
├── TEST_README.md              # 🧪 Testing documentation
└── study_framework_core/
    └── README.md               # 👨‍💻 Developer documentation
```

## 🚀 Ready for Distribution

This structure is now ready for:
- ✅ **Git repository creation**
- ✅ **Private distribution**
- ✅ **Study deployment**
- ✅ **Framework updates**
- ✅ **Testing and validation**

---

**Total Files**: 35 files across 8 directories
**Framework**: Complete modular data collection study backend
**Distribution**: Private Git repository
**Updates**: Automated via `update_core.py`
