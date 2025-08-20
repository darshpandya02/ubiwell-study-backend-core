"""
Base data processing classes for the study framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import json
import time
import logging


class DataProcessorBase(ABC):
    """
    Base class for data processing functionality.
    
    This class defines the interface that all study-specific data processors must implement.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def process_phone_data(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process phone data for a user.
        
        Args:
            user_id: User identifier
            data: Raw phone data
            
        Returns:
            Processed data
        """
        try:
            # Get configuration
            from study_framework_core.core.config import get_config
            config = get_config()
            
            # Create processed data directory
            processed_dir = os.path.join(config.paths.data_processed_path, str(user_id))
            os.makedirs(processed_dir, exist_ok=True)
            
            # Basic processing - study-specific implementations can override
            processed_data = {
                'user_id': user_id,
                'processed_at': time.time(),
                'data_type': 'phone_data',
                'original_data': data,
                'processed_data': self._basic_phone_processing(data)
            }
            
            # Save processed data
            timestamp = int(time.time())
            filename = f"phone_data_{timestamp}.json"
            file_path = os.path.join(processed_dir, filename)
            
            with open(file_path, 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            return processed_data
            
        except Exception as e:
            logging.error(f"Error processing phone data for user {user_id}: {e}")
            return {'error': str(e)}
    
    def _basic_phone_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic phone data processing - can be overridden by study-specific implementations."""
        return {
            'location_data': data.get('location', []),
            'app_usage_data': data.get('app_usage', []),
            'sensor_data': data.get('sensors', []),
            'processed_timestamp': time.time()
        }
    
    def process_sensor_data(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process sensor data for a user.
        
        Args:
            user_id: User identifier
            data: Raw sensor data
            
        Returns:
            Processed data
        """
        try:
            # Get configuration
            from study_framework_core.core.config import get_config
            config = get_config()
            
            # Create processed data directory
            processed_dir = os.path.join(config.paths.data_processed_path, str(user_id))
            os.makedirs(processed_dir, exist_ok=True)
            
            # Basic processing - study-specific implementations can override
            processed_data = {
                'user_id': user_id,
                'processed_at': time.time(),
                'data_type': 'sensor_data',
                'original_data': data,
                'processed_data': self._basic_sensor_processing(data)
            }
            
            # Save processed data
            timestamp = int(time.time())
            filename = f"sensor_data_{timestamp}.json"
            file_path = os.path.join(processed_dir, filename)
            
            with open(file_path, 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            return processed_data
            
        except Exception as e:
            logging.error(f"Error processing sensor data for user {user_id}: {e}")
            return {'error': str(e)}
    
    def _basic_sensor_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic sensor data processing - can be overridden by study-specific implementations."""
        return {
            'accelerometer_data': data.get('accelerometer', []),
            'gyroscope_data': data.get('gyroscope', []),
            'heart_rate_data': data.get('heart_rate', []),
            'processed_timestamp': time.time()
        }
    
    def generate_daily_summary(self, uid: str, date: datetime) -> Dict[str, Any]:
        """
        Generate daily summary for a user and date.
        
        Args:
            uid: User ID
            date: Date to generate summary for
            
        Returns:
            Daily summary data
        """
        try:
            # Get configuration and database
            from study_framework_core.core.config import get_config
            config = get_config()
            db = get_db()
            
            start_time = date.timestamp()
            end_time = (date + timedelta(days=1)).timestamp()
            
            # Get location data
            distance, location_duration = self._get_location_info(db, uid, start_time, end_time)
            
            # Get sensor data
            empatica_duration, stress_duration = self._get_sensor_info(db, uid, start_time, end_time)
            
            # Get EMA data
            scheduled_emas, completed_emas, depression_scores = self._get_ema_info(db, uid, start_time, end_time)
            
            # Get app usage data
            app_info, total_app_events = self._get_app_usage_info(db, uid, start_time, end_time)
            
            # Create summary record
            summary = {
                'uid': uid,
                'date': start_time,
                'date_obj': date,
                'distance': distance,
                'location_duration': location_duration,
                'empatica_duration': empatica_duration,
                'stress_duration': stress_duration,
                'scheduled_emas': scheduled_emas,
                'completed_emas': completed_emas,
                'total_app_events': total_app_events,
                'app_events_info': app_info,
                'depression_scores': depression_scores
            }
            
            # Save to database
            self._save_daily_summary(db, summary)
            
            return summary
            
        except Exception as e:
            logging.error(f"Error generating daily summary for user {uid}: {e}")
            return {'error': str(e)}
    
    def _get_location_info(self, db, uid: str, start_time: float, end_time: float) -> tuple:
        """Get location and distance information."""
        try:
            # Get GPS records
            gps_records = db['ios_location'].find({
                'uid': uid, 
                'event_id': 152, 
                'timestamp': {'$gte': start_time, '$lt': end_time}
            }).sort('timestamp', 1)
            
            location_trace = []
            for record in gps_records:
                location_trace.append({
                    'time': datetime.fromtimestamp(record['timestamp']),
                    'lat': record['latitude'],
                    'lon': record['longitude']
                })
            
            # Calculate distance
            distance = self._calculate_distance_traveled(location_trace)
            
            # Calculate duration (simplified)
            duration = len(location_trace) * 10 / 60  # 10 minutes per GPS point
            
            return distance, duration
            
        except Exception as e:
            logging.error(f"Error getting location info for user {uid}: {e}")
            return 0.0, 0.0
    
    def _get_sensor_info(self, db, uid: str, start_time: float, end_time: float) -> tuple:
        """Get sensor data information."""
        try:
            # Count sensor records
            empatica_count = db['garmin_hr'].count_documents({
                'uid': uid, 
                'timestamp': {'$gte': start_time, '$lt': end_time}
            })
            stress_count = db['garmin_stress'].count_documents({
                'uid': uid, 
                'timestamp': {'$gte': start_time, '$lt': end_time}
            })
            
            # Convert to hours (assuming 6-minute intervals)
            empatica_duration = float(empatica_count) / (6 * 60)
            stress_duration = float(stress_count) / (6 * 60)
            
            return empatica_duration, stress_duration
            
        except Exception as e:
            logging.error(f"Error getting sensor info for user {uid}: {e}")
            return 0.0, 0.0
    
    def _get_ema_info(self, db, uid: str, start_time: float, end_time: float) -> tuple:
        """Get EMA information."""
        try:
            # Get EMA status events
            ema_records = list(db['ema_status_events'].find({
                'uid': uid, 
                'timestamp': {'$gte': start_time, '$lt': end_time}
            }).sort('timestamp', 1))
            
            # Get EMA responses
            ema_responses = list(db['ema_response'].find({
                'uid': uid, 
                'timestamp': {'$gte': start_time, '$lt': end_time}
            }).sort('timestamp', 1))
            
            scheduled_emas = []
            completed_emas = []
            depression_scores = {}
            
            for record in ema_records:
                if record["status"] == "scheduled":
                    scheduled_emas.append(record["ema_id"])
                elif record["status"] == "completed":
                    completed_emas.append(record["ema_id"])
                    
                    # Look for depression scores in responses
                    for response in ema_responses:
                        if response.get('ema_id') == record["ema_id"]:
                            # Parse depression score (simplified)
                            depression_scores[record["ema_id"]] = self._extract_depression_score(response)
                            break
            
            return list(set(scheduled_emas)), completed_emas, depression_scores
            
        except Exception as e:
            logging.error(f"Error getting EMA info for user {uid}: {e}")
            return [], [], {}
    
    def _get_app_usage_info(self, db, uid: str, start_time: float, end_time: float) -> tuple:
        """Get app usage information."""
        try:
            app_records = list(db['app_usage_logs'].find({
                'uid': uid, 
                'timestamp': {'$gte': start_time, '$lt': end_time}
            }).sort('timestamp', 1))
            
            app_info = {}
            total_events = 0
            
            for record in app_records:
                total_events += 1
                app_name = record.get('appName', 'unknown')
                
                if app_name not in app_info:
                    app_info[app_name] = {'open': 0, 'close': 0}
                
                if record["status"] == "open":
                    app_info[app_name]['open'] += 1
                else:
                    app_info[app_name]['close'] += 1
            
            return app_info, total_events
            
        except Exception as e:
            logging.error(f"Error getting app usage info for user {uid}: {e}")
            return {}, 0
    
    def _calculate_distance_traveled(self, location_trace: List[Dict]) -> float:
        """Calculate total distance traveled from location trace."""
        try:
            if len(location_trace) < 2:
                return 0.0
            
            total_distance = 0.0
            for i in range(1, len(location_trace)):
                prev = location_trace[i-1]
                curr = location_trace[i]
                
                # Simple distance calculation (can be improved with geopy)
                lat_diff = curr['lat'] - prev['lat']
                lon_diff = curr['lon'] - prev['lon']
                distance = (lat_diff**2 + lon_diff**2)**0.5 * 111000  # Rough conversion to meters
                
                total_distance += distance
            
            return total_distance / 1000  # Convert to kilometers
            
        except Exception as e:
            logging.error(f"Error calculating distance: {e}")
            return 0.0
    
    def _extract_depression_score(self, response: Dict) -> str:
        """Extract depression score from EMA response."""
        try:
            # This is a simplified implementation
            # In practice, you'd parse the actual EMA response structure
            return response.get('depression_score', '0')
        except Exception as e:
            logging.error(f"Error extracting depression score: {e}")
            return '0'
    
    def _save_daily_summary(self, db, summary: Dict[str, Any]):
        """Save daily summary to database."""
        try:
            db['daily_summaries'].update_one(
                {'uid': summary['uid'], 'date': summary['date']}, 
                {"$set": summary}, 
                upsert=True
            )
            logging.info(f"Saved daily summary for user {summary['uid']} on {summary['date']}")
        except Exception as e:
            logging.error(f"Error saving daily summary: {e}")
            raise
    

    
    @abstractmethod
    def generate_visualizations(self, user_id: str, date: datetime) -> Dict[str, str]:
        """
        Generate visualizations for a user.
        
        Args:
            user_id: User identifier
            date: Date for visualizations
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        pass
