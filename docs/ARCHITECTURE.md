# Architecture Guide

This document provides a comprehensive overview of the Study Framework Core architecture.

## Problem Statement

You currently have a monolithic backend system for data collection studies that requires cloning and modifying the entire codebase for each new study. This approach has several issues:

1. **Code Duplication**: Each study is a complete copy of the codebase
2. **Maintenance Overhead**: Bug fixes and updates must be applied to each study individually
3. **Inconsistent Features**: Different studies may have different versions of core functionality
4. **Deployment Complexity**: Setting up a new study requires significant manual work
5. **Limited Customization**: Study-specific features are mixed with core functionality

## Solution: Modular Study Framework

The proposed solution creates a **modular framework** that separates core functionality from study-specific customizations, enabling:

- **Centralized Core**: Common functionality is maintained in a single, versioned package
- **Easy Updates**: Core improvements automatically propagate to all studies
- **Study-Specific Customization**: Each study can add custom features without affecting others
- **Rapid Deployment**: New studies can be created quickly using the framework
- **Consistent Architecture**: All studies follow the same patterns and conventions

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Study Framework Core                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Dashboard     │  │       API       │  │   Data       │ │
│  │     Base        │  │      Base       │  │ Processing   │ │
│  │   Classes       │  │    Classes      │  │    Base      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Core          │  │   Core          │  │   Core       │ │
│  │  Templates      │  │   Static        │  │   Config     │ │
│  │                 │  │   Files         │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Study-Specific Implementation                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Connect       │  │   Connect       │  │   Connect    │ │
│  │   Study         │  │   Study         │  │   Study      │ │
│  │   Dashboard     │  │      API        │  │   Data       │ │
│  │                 │  │                 │  │  Processor   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Study-        │  │   Study-        │  │   Study-     │ │
│  │   Specific      │  │   Specific      │  │   Specific   │ │
│  │   Templates     │  │   Static        │  │   Config     │ │
│  │                 │  │   Files         │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Dashboard Framework

**Base Classes:**
- `DashboardBase`: Abstract base class defining dashboard interface
- `DashboardColumn`: Data class for column configuration

**Core Features:**
- Standard columns (User, Phone Duration, Garmin Worn, etc.)
- Extensible column system for study-specific data
- Template-based rendering with core templates
- Sorting and filtering capabilities

**Study-Specific Extension:**
```python
class ConnectStudyDashboard(DashboardBase):
    def _get_custom_columns(self):
        return [
            DashboardColumn("ema_responses", "EMA Responses"),
            DashboardColumn("app_events", "App Events"),
            DashboardColumn("daily_diary", "Daily Diary"),
            DashboardColumn("depression_scores", "Depression Scores"),
        ]
```

### 2. API Framework

**Base Classes:**
- `APIBase`: Abstract base class for API functionality
- `CoreAPIEndpoints`: Standard API endpoints common to all studies

**Core Features:**
- Standard API endpoints (login, upload, data retrieval)
- Authentication and authorization
- Error handling and response formatting

**Study-Specific Extension:**
```python
class ConnectStudyAPI(APIBase):
    def setup_routes(self):
        # Setup core routes
        core_endpoints = CoreAPIEndpoints(self.api, self.auth_key)
        
        # Add Connect Study specific endpoints
        self.api.add_resource(RequestEmaFile, '/data/ema-request')
        self.api.add_resource(UploadDailyDiary, '/data/daily-diary')
        self.api.add_resource(UploadEma, '/data/ema-response')
```

### 3. Data Processing Framework

**Base Classes:**
- `DataProcessorBase`: Abstract base class for data processing

**Core Features:**
- Standard data processing pipelines
- Daily summary generation
- Visualization creation
- Database operations

**Study-Specific Extension:**
```python
class ConnectStudyDataProcessor(DataProcessorBase):
    def process_phone_data(self, user_id, data):
        # Study-specific phone data processing
        return processed_data
```

## Template System

### Core Templates
- `dashboard_base.html`: Flexible dashboard template
- `navigation.html`: Standard navigation component
- Core CSS and JavaScript files

### Study-Specific Templates
Studies can extend core templates or create their own:

```html
{% extends "study_framework_core:templates/dashboard_base.html" %}

{% block extra_css %}
<link rel="stylesheet" href="/static/css/connect_study_styles.css">
{% endblock %}

{% block extra_js %}
<script src="/static/js/connect_study_dashboard.js"></script>
{% endblock %}
```

## Configuration System

### Core Configuration
- Database connections
- Authentication settings
- Standard paths and URLs

### Study-Specific Configuration
```python
STUDY_CONFIG = {
    "name": "Connect Study",
    "database": "connect_study_db",
    "tokens": ["your-auth-token"],
    "custom_columns": ["ema_responses", "app_events", "daily_diary"],
    "data_paths": {
        "phone_data": "/path/to/phone/data",
        "sensor_data": "/path/to/sensor/data",
    }
}
```

## Migration Process

### Current State → New Framework

1. **Extract Core Functionality**
   - Identify common features across studies
   - Create base classes and interfaces
   - Move shared templates and static files

2. **Create Study-Specific Implementation**
   - Extend base classes with study-specific logic
   - Implement custom columns and features
   - Configure study-specific settings

3. **Update Application Structure**
   - Replace monolithic structure with modular approach
   - Use dependency injection for study-specific components
   - Maintain backward compatibility during transition

### Example: Connect Study Migration

**Before (Monolithic):**
```python
# Single file with all functionality mixed together
def generate_page_html(token, date_str):
    # Core functionality + Connect Study specific logic
    # Hard to separate and reuse
```

**After (Modular):**
```python
# Core framework provides base functionality
class DashboardBase:
    def generate_core_row_data(self, user_data, date_str):
        # Standard columns for all studies
        pass

# Connect Study extends with custom features
class ConnectStudyDashboard(DashboardBase):
    def generate_custom_row_data(self, user_data, date_str):
        # Connect Study specific columns
        return {
            "ema_responses": self._get_ema_data(user_data),
            "app_events": self._get_app_events(user_data),
            "daily_diary": self._check_daily_diary(user_data),
            "depression_scores": self._get_depression_scores(user_data),
        }
```

## Benefits

### 1. Maintainability
- **Centralized Updates**: Core improvements benefit all studies
- **Reduced Duplication**: Common code is maintained once
- **Consistent Architecture**: All studies follow the same patterns

### 2. Flexibility
- **Easy Customization**: Studies can add features without affecting others
- **Modular Design**: Components can be mixed and matched
- **Extensible Framework**: New capabilities can be added to the core

### 3. Deployment
- **Rapid Setup**: New studies can be created in minutes
- **Automated Deployment**: Scripts handle boilerplate generation
- **Consistent Configuration**: Standardized setup process

### 4. Development
- **Clear Separation**: Core vs. study-specific code is obvious
- **Reusable Components**: Features can be shared across studies
- **Testing**: Core functionality can be tested independently

## Usage Examples

### Creating a New Study

```bash
# Use the deployment script
python deploy_new_study.py "New Study Name" \
    --custom-columns "EMA Responses" "App Events" "Daily Diary" \
    --tokens "token1" "token2" \
    --database "new_study_db"
```

### Adding Custom Features

```python
# Add a new custom column
class MyStudyDashboard(DashboardBase):
    def _get_custom_columns(self):
        columns = super()._get_custom_columns()
        columns.append(DashboardColumn("custom_metric", "Custom Metric"))
        return columns
    
    def generate_custom_row_data(self, user_data, date_str):
        data = super().generate_custom_row_data(user_data, date_str)
        data["custom_metric"] = self._calculate_custom_metric(user_data)
        return data
```

### Updating Core Framework

```bash
# Update the core framework
pip install --upgrade study-framework-core

# All studies automatically get the new features
# Study-specific customizations remain unchanged
```

## Implementation Roadmap

### Phase 1: Core Framework Development ✅
- [x] Design base classes and interfaces
- [x] Create core templates and static files
- [x] Implement basic dashboard functionality
- [x] Create deployment scripts

### Phase 2: Migration ✅
- [x] Migrate Connect Study to new framework
- [x] Test all functionality
- [x] Update documentation
- [x] Create migration guide

### Phase 3: Deployment ✅
- [x] Deploy core framework to package repository
- [x] Set up automated testing
- [x] Create study templates
- [x] Train team on new framework

### Phase 4: Enhancement
- [ ] Add more core features
- [ ] Improve customization options
- [ ] Add monitoring and analytics
- [ ] Create study comparison tools

## Conclusion

The modular study framework solves the original problem by:

1. **Eliminating Code Duplication**: Core functionality is shared across all studies
2. **Enabling Easy Updates**: Core improvements propagate automatically
3. **Supporting Customization**: Studies can add features without affecting others
4. **Simplifying Deployment**: New studies can be created quickly
5. **Improving Maintainability**: Clear separation of concerns

This architecture provides a sustainable foundation for managing multiple data collection studies while maintaining flexibility for study-specific requirements.

---

**For extension examples, see [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md).**
**For setup instructions, see [SETUP_GUIDE.md](../SETUP_GUIDE.md).**
