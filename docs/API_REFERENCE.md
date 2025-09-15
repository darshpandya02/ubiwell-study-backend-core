# API Reference

This document provides a complete reference for the Study Framework Core API.

## 📚 Core Functions

### **Configuration Functions**
- `get_config()`: Get configuration instance
- `set_config_file(config_file)`: Set configuration file and reload

### **Database Functions**
- `get_db()`: Get database connection
- `get_db_client()`: Get MongoDB client

### **Utility Functions**
- `current_milli_time()`: Get current timestamp in milliseconds

## 🔧 Helper Functions

### **File Operations**
- `allowed_file(filename)`: Check if file type is allowed
- `save_file(file, path)`: Save uploaded file
- `archive_file(file_path, archive_dir)`: Archive processed files

### **Authentication**
- `login_check(token)`: Verify user login
- `login_code_check(token)`: Verify user login with code
- `verify_admin_login(username, password)`: Verify admin login

### **User Management**
- `create_user(uid, password)`: Create new user
- `create_multiple_users(user_list)`: Create multiple users
- `get_all_users()`: Get all users from database
- `export_users_csv()`: Export users to CSV format
- `create_admin_user()`: Create admin user for internal web

### **Data Processing**
- `process_all_data()`: Process all uploaded data
- `generate_all_summaries()`: Generate daily summaries
- `process_garmin_files()`: Process Garmin FIT files

## 📊 Core Classes

### **DashboardBase**

Base class for extensible dashboards.

```python
class DashboardBase:
    def _get_custom_columns(self) -> List[DashboardColumn]:
        """Return list of custom column names."""
        return []
    
    def generate_core_row_data(self, user_data: Dict[str, Any], date_str: str) -> Dict[str, Any]:
        """Generate data for core columns."""
        return {
            "user": user_data["uid"],
            "phone_duration": f"{user_data.get('phone_duration', 0):.2f}",
            "garmin_worn": f"{user_data.get('garmin_worn', 0):.2f}",
            "garmin_on": f"{user_data.get('garmin_on', 0):.2f}",
            "distance_traveled": f"{user_data.get('distance', 0):.2f}",
            "details": f"<a href='/internal_web/dashboard/view/{user_data['uid']}/{date_str}'>Details</a>"
        }
    
    def generate_custom_row_data(self, user_data: Dict[str, Any], date_str: str) -> Dict[str, Any]:
        """Generate data for custom columns."""
        return {}
    
    def get_template_context(self, token: str, date_str: str, users: List[Dict]) -> Dict[str, Any]:
        """Get template context for dashboard rendering."""
        # Implementation details...
```

### **APIBase**

Base class for extensible APIs.

```python
class APIBase(ABC):
    def __init__(self, app: Flask):
        self.app = app
        self.api = Api(app, prefix='/api/v1')
        self.setup_routes()
    
    @abstractmethod
    def setup_routes(self):
        """Setup API routes. Override in study-specific implementations."""
        pass
    
    @abstractmethod
    def verify_user_login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Verify user login credentials."""
        pass
    
    @abstractmethod
    def upload_phone_logs(self, user_id: str, logs: Dict[str, Any]) -> Dict[str, Any]:
        """Upload phone logs for a user."""
        pass
    
    @abstractmethod
    def upload_phone_data(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload phone data for a user."""
        pass
```

### **CoreAPIEndpoints**

Core API endpoints that are common across all studies.

```python
class CoreAPIEndpoints:
    def __init__(self, api: Api, auth_key: str):
        self.api = api
        self.auth_key = auth_key
        self.setup_core_routes()
    
    def setup_core_routes(self):
        """Setup core API routes that are common to all studies."""
        self.api.add_resource(Default, '/')
        self.api.add_resource(HealthCheck, '/health')
        self.api.add_resource(Login, '/credentials/check')
        self.api.add_resource(LoginCode, '/credentials/checkCode')
        self.api.add_resource(UserInfo, '/user/info/update')
        self.api.add_resource(PhonePing, '/user/status/ping')
        self.api.add_resource(UploadFile, '/data/upload')
        self.api.add_resource(UploadLogFile, '/data/uploadLog')
        self.api.add_resource(UploadDailyDiary, '/data/daily-diary')
        self.api.add_resource(UploadEma, '/data/ema-response')
        self.api.add_resource(RequestEmaFile, '/data/ema-request')
        self.api.add_resource(UploadJSON, '/upload-news/')
```

### **DataProcessorBase**

Base class for data processing.

```python
class DataProcessorBase(ABC):
    def __init__(self, config: StudyFrameworkConfig):
        self.config = config
        self.db = get_db()
    
    @abstractmethod
    def process_phone_data(self, user_id: str) -> Dict[str, Any]:
        """Process phone data for a user."""
        pass
    
    @abstractmethod
    def process_garmin_data(self, user_id: str) -> Dict[str, Any]:
        """Process Garmin data for a user."""
        pass
    
    @abstractmethod
    def generate_daily_summary(self, user_id: str, date: str) -> Dict[str, Any]:
        """Generate daily summary for a user."""
        pass
```

## 🔌 API Endpoints

### **Core Endpoints**

#### **Default** (`/`)
```http
GET /api/v1/
```
Returns basic API information.

**Response:**
```json
{
  "message": "Study Framework API",
  "version": "1.0.0"
}
```

#### **Health Check** (`/health`)
```http
GET /api/v1/health
```
Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "study-framework-api"
}
```

#### **Login** (`/credentials/check`)
```http
POST /api/v1/credentials/check
```
Verify user login credentials.

**Request Body:**
```json
{
  "uid": "user123",
  "password": "password123",
  "device": "iPhone",
  "auth_key": "your-auth-key"
}
```

**Response:**
```json
{
  "message": {
    "info": "user_handler success",
    "uid": "user123"
  },
  "status": 200
}
```

#### **Login Code** (`/credentials/checkCode`)
```http
POST /api/v1/credentials/checkCode
```
Verify user login with code.

**Request Body:**
```json
{
  "uid": "user123",
  "code": "123456",
  "auth_key": "your-auth-key"
}
```

#### **User Info Update** (`/user/info/update`)
```http
POST /api/v1/user/info/update
```
Update user information.

**Request Body:**
```json
{
  "uid": "user123",
  "info": {
    "name": "John Doe",
    "age": 25
  },
  "auth_key": "your-auth-key"
}
```

#### **Phone Ping** (`/user/status/ping`)
```http
POST /api/v1/user/status/ping
```
Update user ping status.

**Request Body:**
```json
{
  "uid": "user123",
  "ping": "online",
  "auth_key": "your-auth-key"
}
```

#### **Upload File** (`/data/upload`)
```http
POST /api/v1/data/upload
```
Upload data file.

**Request:**
- `file`: File to upload
- `uid`: User ID
- `auth_key`: Authentication key

#### **Upload Log File** (`/data/uploadLog`)
```http
POST /api/v1/data/uploadLog
```
Upload log file.

**Request:**
- `file`: Log file to upload
- `uid`: User ID
- `auth_key`: Authentication key

#### **Upload Daily Diary** (`/data/daily-diary`)
```http
POST /api/v1/data/daily-diary
```
Upload daily diary data.

**Request Body:**
```json
{
  "uid": "user123",
  "diary_data": {
    "mood": "happy",
    "activities": ["work", "exercise"]
  },
  "auth_key": "your-auth-key"
}
```

#### **Upload EMA Response** (`/data/ema-response`)
```http
POST /api/v1/data/ema-response
```
Upload EMA (Ecological Momentary Assessment) response.

**Request Body:**
```json
{
  "uid": "user123",
  "ema_data": {
    "survey_id": "morning_survey",
    "responses": {
      "mood": 8,
      "energy": 7
    }
  },
  "auth_key": "your-auth-key"
}
```

#### **Request EMA File** (`/data/ema-request`)
```http
GET /api/v1/data/ema-request
```
Request EMA file for user.

**Query Parameters:**
- `uid`: User ID
- `auth_key`: Authentication key

#### **Upload JSON** (`/upload-news/`)
```http
POST /api/v1/upload-news/
```
Upload JSON data.

**Request Body:**
```json
{
  "uid": "user123",
  "data": {
    "type": "news",
    "content": "Sample content"
  },
  "auth_key": "your-auth-key"
}
```

## 📋 Schemas

### **LoginSchema**
```python
class LoginSchema(Schema):
    uid = fields.Str(required=True)
    password = fields.Str(required=True)
    device = fields.Str(required=True)
    auth_key = fields.Str(required=True)
```

### **LoginCodeSchema**
```python
class LoginCodeSchema(Schema):
    uid = fields.Str(required=True)
    code = fields.Str(required=True)
    auth_key = fields.Str(required=True)
```

### **UserInfoSchema**
```python
class UserInfoSchema(Schema):
    uid = fields.Str(required=True)
    info = fields.Dict(required=True)
    auth_key = fields.Str(required=True)
```

### **UserPingSchema**
```python
class UserPingSchema(Schema):
    uid = fields.Str(required=True)
    ping = fields.Str(required=True)
    auth_key = fields.Str(required=True)
```

### **EMASchema**
```python
class EMASchema(Schema):
    uid = fields.Str(required=True)
    ema_data = fields.Dict(required=True)
    auth_key = fields.Str(required=True)
```

### **UploadFileSchema**
```python
class UploadFileSchema(Schema):
    uid = fields.Str(required=True)
    auth_key = fields.Str(required=True)
```

### **DebugSchema**
```python
class DebugSchema(Schema):
    uid = fields.Str(required=True)
    auth_key = fields.Str(required=True)
```

### **SocialMediaSchema**
```python
class SocialMediaSchema(Schema):
    uid = fields.Str(required=True)
    social_data = fields.Dict(required=True)
    auth_key = fields.Str(required=True)
```

## 🔧 Configuration

### **StudyFrameworkConfig**

Main configuration class that provides access to all configuration sections.

```python
class StudyFrameworkConfig:
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._load_config()
    
    # Configuration sections
    database: DatabaseConfig
    server: ServerConfig
    logging: LoggingConfig
    collections: CollectionNames
    security: SecurityConfig
    paths: PathsConfig
    
    def get_database_url(self) -> str:
        """Get MongoDB connection URL."""
        pass
    
    def get_log_file_path(self, component: str) -> str:
        """Get log file path for a specific component."""
        pass
    
    def get_socket_path(self, component: str) -> str:
        """Get socket path for a specific component."""
        pass
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        pass
    
    def save_config(self, config_file: Optional[str] = None):
        """Save current configuration to file."""
        pass
```

### **DatabaseConfig**
```python
@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 27017
    username: Optional[str] = None
    password: Optional[str] = None
    database: str = "study_db"
    auth_source: str = "admin"
    auth_mechanism: str = "SCRAM-SHA-1"
```

### **ServerConfig**
```python
@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    workers: int = 3
    timeout: int = 120
    socket_path: Optional[str] = None
```

### **SecurityConfig**
```python
@dataclass
class SecurityConfig:
    secret_key: Optional[str] = None
    auth_key: str = "your-auth-key"
    tokens: list = None
    allowed_ips: list = None
    cors_origins: list = None
    announcement_pass_key: str = "study123"
```

### **PathsConfig**
```python
@dataclass
class PathsConfig:
    base_dir: str = "/mnt/study"
    data_dir: str = "/mnt/study/data"
    logs_dir: str = "/mnt/study/logs"
    sockets_dir: str = "/var/sockets"
    static_dir: str = "/mnt/study/static"
    uploads_dir: str = "/mnt/study/uploads"
    data_upload_path: str = "/mnt/study/data_uploads/uploads"
    data_processed_path: str = "/mnt/study/data_uploads/processed"
    data_exceptions_path: str = "/mnt/study/data_uploads/exceptions"
    data_upload_logs_path: str = "/mnt/study/data_uploads/logs"
    active_sensing_upload_path: str = "/mnt/study/active_sensing"
    ema_file_path: str = "/mnt/study/ema_surveys"
    config_dir: str = "/mnt/study/config-files"
```

## 📊 Collection Names

Centralized collection names for MongoDB collections.

```python
class CollectionNames:
    # iOS data collections
    IOS_LOCATION = 'ios_location'
    IOS_BRIGHTNESS = 'ios_brightness'
    IOS_BLUETOOTH = 'ios_bluetooth'
    IOS_WIFI = 'ios_wifi'
    IOS_BATTERY = 'ios_battery'
    IOS_LOCK_UNLOCK = 'ios_lock_unlock'
    IOS_STEPS = 'ios_steps'
    IOS_ACTIVITY = 'ios_activity'
    IOS_ACCELEROMETER = 'ios_accelerometer'
    IOS_CALLLOG = 'ios_calllog'
    
    # Garmin data collections
    GARMIN_HR = 'garmin_hr'
    GARMIN_STRESS = 'garmin_stress'
    GARMIN_IBI = 'garmin_ibi'
    GARMIN_RESPIRATION = 'garmin_respiration'
    GARMIN_STEPS = 'garmin_steps'
    GARMIN_ENERGY = 'garmin_energy'
    
    # App and EMA collections
    EMA_RESPONSE = "ema_response"
    EMA_STATUS_EVENTS = "ema_status_events"
    APP_USAGE_LOGS = "app_usage_logs"
    NOTIFICATION_EVENTS = "notification_events"
    APP_SCREEN_EVENTS = "app_screen_events"
    
    # Summary collections
    DAILY_SUMMARY = 'daily_summaries'
    
    # Unknown events collection
    UNKNOWN_EVENTS = 'unknown_events_data'
    
    # User collections
    USERS = 'users'
    USER_CODE_MAPPINGS = 'user_code_mappings'
```

## 🐛 Error Handling

### **Standard Response Format**
All API endpoints return responses in a standard format:

```json
{
  "message": "Response message or data",
  "status": 200
}
```

### **Error Codes**
- `200`: Success
- `400`: Bad Request (invalid input)
- `401`: Unauthorized (invalid credentials)
- `403`: Forbidden (not permitted)
- `404`: Not Found
- `405`: Method Not Allowed
- `500`: Internal Server Error

### **Validation Errors**
When request validation fails, the response includes detailed error messages:

```json
{
  "message": {
    "uid": ["Missing data for required field."],
    "auth_key": ["Missing data for required field."]
  },
  "status": 400
}
```

---

**For extension examples, see [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md).**
**For setup instructions, see [SETUP_GUIDE.md](../SETUP_GUIDE.md).**


