"""
Example: Study implementation using centralized configuration.

This shows how to use the centralized configuration system in a study-specific implementation.
"""

from study_framework_core.core import (
    DashboardBase, 
    DashboardColumn, 
    APIBase, 
    DataProcessorBase,
    get_config
)
from flask import Flask, request, jsonify
from typing import Dict, List, Any
import logging


class ExampleStudyDashboard(DashboardBase):
    """Example study dashboard using centralized configuration."""
    
    def __init__(self):
        super().__init__()
        # Get configuration
        self.config = get_config()
        
        # Setup logging using config
        logging.basicConfig(
            level=getattr(logging, self.config.logging.level),
            format=self.config.logging.format,
            filename=self.config.get_log_file_path('dashboard')
        )
    
    def _get_custom_columns(self) -> List[DashboardColumn]:
        """Get study-specific custom columns."""
        return [
            DashboardColumn("custom_metric", "Custom Metric", width="10%"),
        ]
    
    def generate_core_row_data(self, user_data: Dict[str, Any], date_str: str) -> Dict[str, Any]:
        """Generate data for core columns."""
        # Use configuration for paths and settings
        base_url = self.config.paths.base_dir
        
        return {
            "user": user_data["uid"],
            "phone_duration": f"{user_data.get('phone_duration', 0):.2f}",
            "garmin_worn": f"{user_data.get('garmin_worn', 0):.2f}",
            "garmin_on": f"{user_data.get('garmin_on', 0):.2f}",
            "distance_traveled": f"{user_data.get('distance', 0):.2f}",
            "details": f"<a href='{base_url}/details/{user_data['uid']}/{date_str}'>Details</a>"
        }
    
    def generate_custom_row_data(self, user_data: Dict[str, Any], date_str: str) -> Dict[str, Any]:
        """Generate data for custom columns."""
        return {
            "custom_metric": user_data.get('custom_metric', 'N/A')
        }


class ExampleStudyAPI(APIBase):
    """Example study API using centralized configuration."""
    
    def __init__(self, app: Flask):
        self.config = get_config()
        super().__init__(app)
    
    def setup_routes(self):
        """Setup study-specific routes."""
        @self.app.route('/api/v1/upload', methods=['POST'])
        def upload_data():
            # Use configuration for validation
            if not self._validate_token(request.headers.get('Authorization')):
                return jsonify({'error': 'Invalid token'}), 401
            
            # Use configuration for file paths
            upload_dir = self.config.paths.uploads_dir
            # ... handle upload logic
            
            return jsonify({'success': True})
    
    def verify_user_login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Verify user login using configuration."""
        # Use tokens from configuration
        if credentials.get('token') in self.config.security.tokens:
            return {'success': True, 'user_id': credentials.get('user_id')}
        return {'success': False, 'error': 'Invalid token'}
    
    def upload_phone_logs(self, user_id: str, logs: Dict[str, Any]) -> Dict[str, Any]:
        """Upload phone logs using configuration."""
        # Use configuration for paths
        log_file = self.config.get_log_file_path('phone_logs')
        # ... handle log upload
        
        return {'success': True, 'message': 'Logs uploaded'}
    
    def upload_phone_data(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload phone data using configuration."""
        # Use configuration for data directory
        data_dir = self.config.paths.data_dir
        # ... handle data upload
        
        return {'success': True, 'message': 'Data uploaded'}
    
    def _validate_token(self, auth_header: str) -> bool:
        """Validate token using configuration."""
        if not auth_header:
            return False
        
        token = auth_header.replace('Bearer ', '')
        return token in self.config.security.tokens


class ExampleStudyDataProcessor(DataProcessorBase):
    """Example study data processor using centralized configuration."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.framework_config = get_config()
    
    def process_phone_data(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process phone data using configuration."""
        # Use configuration for processing settings
        processed_data = {
            'user_id': user_id,
            'data': data,
            'processed_at': 'timestamp',
            'output_dir': self.framework_config.paths.data_dir
        }
        
        return processed_data
    
    def process_sensor_data(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process sensor data using configuration."""
        return self.process_phone_data(user_id, data)
    
    def generate_daily_summary(self, user_id: str, date) -> Dict[str, Any]:
        """Generate daily summary using configuration."""
        summary = {
            'user_id': user_id,
            'date': date,
            'summary_file': self.framework_config.get_log_file_path('daily_summary')
        }
        
        return summary
    
    def generate_visualizations(self, user_id: str, date) -> Dict[str, str]:
        """Generate visualizations using configuration."""
        static_dir = self.framework_config.paths.static_dir
        return {
            'daily_activity': f'{static_dir}/plots/{user_id}_{date.strftime("%Y%m%d")}_activity.png'
        }


# Example Flask application using centralized configuration
def create_app():
    """Create Flask application with centralized configuration."""
    app = Flask(__name__)
    
    # Get configuration
    config = get_config()
    
    # Set Flask configuration from framework config
    app.config['SECRET_KEY'] = config.security.secret_key or 'default-secret-key'
    app.config['DEBUG'] = config.server.debug
    
    # Initialize study components
    dashboard = ExampleStudyDashboard()
    api = ExampleStudyAPI(app)
    processor = ExampleStudyDataProcessor({})
    
    # Store components in app context
    app.dashboard = dashboard
    app.api = api
    app.processor = processor
    
    return app


if __name__ == "__main__":
    # Example usage
    app = create_app()
    
    # Access configuration anywhere in the application
    config = get_config()
    print(f"Database URL: {config.get_database_url()}")
    print(f"Log file: {config.get_log_file_path('app')}")
    print(f"Socket path: {config.get_socket_path('example_study')}")
    
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug
    )
