"""
Backend processing scripts for the study framework.
Handles data processing, Garmin FIT files, daily summaries, and data visualization.
"""

import os
import sys
import subprocess
import logging
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from collections import defaultdict

import pandas as pd
import pymongo
from geopy import distance

from study_framework_core.core.config import get_config
from study_framework_core.core.handlers import get_db


class DataProcessor:
    """Main data processor for handling all backend processing tasks."""
    
    def __init__(self):
        self.config = get_config()
        self.db = get_db()
        self.records = {}  # For batch processing
        self.batch_size = 2000  # Batch size for bulk inserts
        self.setup_logging()
        self.init_collections()  # Initialize collections with indexes
    
    def setup_logging(self):
        """Setup logging for data processing."""
        # Debug: Print config paths
        print(f"DEBUG: Config paths:")
        print(f"  base_dir: {self.config.paths.base_dir}")
        print(f"  logs_dir: {self.config.paths.logs_dir}")
        print(f"  data_dir: {self.config.paths.data_dir}")
        
        # Ensure logs directory exists
        logs_dir = Path(self.config.paths.logs_dir)
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "data_processing.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_collections(self):
        """Initialize MongoDB collections with indexes for optimal performance."""
        try:
            import pymongo
            
            # iOS data collections
            self.db[self.config.collections.IOS_LOCATION].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING),
                ('event_id', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_WIFI].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING),
                ('event_id', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_BLUETOOTH].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_BRIGHTNESS].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_LOCK_UNLOCK].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_BATTERY].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_ACTIVITY].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_STEPS].create_index([
                ('uid', pymongo.ASCENDING),
                ('start_timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_ACCELEROMETER].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.IOS_CALLLOG].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.UNKNOWN_EVENTS].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            # Garmin data collections
            self.db[self.config.collections.GARMIN_HR].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.GARMIN_STRESS].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.GARMIN_STEPS].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.GARMIN_RESPIRATION].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.GARMIN_IBI].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.GARMIN_ENERGY].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            # EmpaTica data collections
            self.db[self.config.collections.EMPATICA_EDA].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.EMPATICA_TEMPERATURE].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.EMPATICA_IBI].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.EMPATICA_BATTERY].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.EMPATICA_BVP].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            # App and EMA collections
            self.db[self.config.collections.EMA_RESPONSE].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.EMA_STATUS_EVENTS].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.APP_USAGE_LOGS].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.NOTIFICATION_EVENTS].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.APP_SCREEN_EVENTS].create_index([
                ('uid', pymongo.ASCENDING),
                ('timestamp', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            # Summary collections
            self.db[self.config.collections.DAILY_SUMMARY].create_index([
                ('uid', pymongo.ASCENDING),
                ('date', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            # User collections
            self.db[self.config.collections.USERS].create_index([
                ('uid', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.db[self.config.collections.USER_CODE_MAPPINGS].create_index([
                ('uid', pymongo.ASCENDING),
                ('uid_code', pymongo.ASCENDING)
            ], unique=True, dropDups=True)
            
            self.logger.info("Successfully initialized MongoDB collections with indexes")
            
        except Exception as e:
            self.logger.error(f"Error initializing collections: {e}")
    
    def add_record(self, collection: str, record: dict):
        """Add a record to the batch processing queue."""
        if collection not in self.records:
            self.records[collection] = []
        self.records[collection].append(record)
        
        # Flush batch if it reaches the batch size
        if len(self.records[collection]) >= self.batch_size:
            self.flush_records(collection)
    
    def flush_records(self, collection: str = None):
        """Flush records to MongoDB using bulk insert."""
        try:
            if collection:
                collections_to_flush = [collection]
            else:
                collections_to_flush = list(self.records.keys())
            
            for coll in collections_to_flush:
                if coll in self.records and self.records[coll]:
                    self.db[coll].insert_many(self.records[coll], ordered=False)
                    self.logger.info(f"Bulk inserted {len(self.records[coll])} records to {coll}")
                    self.records[coll].clear()
                    
        except Exception as e:
            self.logger.error(f"Error flushing records to {collection}: {e}")
    
    def archive_file(self, user: str, file_path: str):
        """Move processed file from upload to processed directory."""
        try:
            archive_dir = Path(self.config.paths.data_processed_path) / "phone" / user
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            file_name = Path(file_path).name
            archive_path = archive_dir / file_name
            
            shutil.move(file_path, archive_path)
            self.logger.info(f"Archived file: {file_path} -> {archive_path}")
            
        except Exception as e:
            self.logger.error(f"Error archiving file {file_path}: {e}")
    
    def process_garmin_fit_file(self, user: str, input_file: str, 
                               output_path: Optional[str] = None,
                               types_to_process: Optional[str] = None,
                               separate_types: bool = True,
                               date_time_format: Optional[str] = None) -> bool:
        """
        Process a single Garmin FIT/SDK file to CSV format using the CLI JAR.
        
        Args:
            user: User ID
            input_file: Path to the FIT/SDK file to process
            output_path: Directory where CSV files will be saved
            types_to_process: Comma-separated list of types to process
            separate_types: If True, each data type gets separate file
            date_time_format: Format for timestamps
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Check if JAR file exists (in the core framework)
            jar_path = Path(__file__).parent / "processing" / "load_files" / "fit-processing-cli.jar"
            if not jar_path.exists():
                self.logger.error(f"JAR file not found: {jar_path}")
                return False
            
            # Check if input file exists
            input_path = Path(input_file)
            if not input_path.exists():
                self.logger.error(f"Input file not found: {input_file}")
                return False
            
            # Set output path
            if output_path is None:
                output_path = Path(self.config.paths.data_processed_path) / "garmin" / user
            else:
                output_path = Path(output_path)
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Processing Garmin FIT file: {input_file}")
            
            # Build the Java command
            cmd = [
                "java",
                "-jar",
                str(jar_path),
                str(input_path),
                "--output_file", str(output_path),
                "--output_format", "CSV"
            ]
            
            # Add optional parameters
            if types_to_process:
                cmd.extend(["--types_to_process", types_to_process])
            
            if date_time_format:
                cmd.extend(["--date_time_format", date_time_format])
            
            # Execute the command
            self.logger.info(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully converted FIT to CSV: {input_file}")
                
                # Now process the CSV files and load into MongoDB
                csv_success = self._process_garmin_csv_files(user, output_path)
                
                if csv_success:
                    self.logger.info(f"Successfully loaded Garmin data to MongoDB for: {input_file}")
                    return True
                else:
                    self.logger.error(f"Failed to load CSV data to MongoDB for: {input_file}")
                    return False
            else:
                self.logger.error(f"Error processing {input_file}")
                self.logger.error(f"Return code: {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception processing Garmin file: {e}")
            return False
    
    def _process_garmin_csv_files(self, user: str, csv_directory: Path) -> bool:
        """Process CSV files generated from Garmin FIT files and load into MongoDB."""
        try:
            import pandas as pd
            
            self.logger.info(f"Processing CSV files in directory: {csv_directory}")
            
            if not csv_directory.exists():
                self.logger.error(f"CSV directory not found: {csv_directory}")
                return False
            
            if not csv_directory.is_dir():
                self.logger.error(f"Path is not a directory: {csv_directory}")
                return False
            
            records = []
            
            # List all CSV files found
            csv_files = list(csv_directory.glob("*.csv"))
            self.logger.info(f"Found {len(csv_files)} CSV files: {[f.name for f in csv_files]}")
            
            for csv_file in csv_files:
                self.logger.info(f"Processing CSV file: {csv_file}")
                try:
                    if "ACCELEROMETER" in csv_file.name:
                        acc_df = pd.read_csv(csv_file)
                        for row in acc_df.itertuples(index=False):
                            record = self._handle_garmin_accelerometer(user, row)
                            if record:
                                records.append(record)
                    
                    elif "BBI" in csv_file.name:
                        self.logger.info(f"Processing BBI data for user {user} in file {csv_file}")
                        bbi_df = pd.read_csv(csv_file)
                        for row in bbi_df.itertuples(index=False):
                            record = self._handle_garmin_ibi(user, row)
                            if record:
                                records.append(record)
                    
                    elif "HEART_RATE" in csv_file.name:
                        hr_df = pd.read_csv(csv_file)
                        for row in hr_df.itertuples(index=False):
                            record = self._handle_garmin_hr(user, row)
                            if record:
                                records.append(record)
                    
                    elif "RESPIRATION" in csv_file.name:
                        resp_df = pd.read_csv(csv_file)
                        for row in resp_df.itertuples(index=False):
                            record = self._handle_garmin_respiration(user, row)
                            if record:
                                records.append(record)
                    
                    elif "STEPS" in csv_file.name:
                        steps_df = pd.read_csv(csv_file)
                        for row in steps_df.itertuples(index=False):
                            record = self._handle_garmin_steps(user, row)
                            if record:
                                records.append(record)
                    
                    elif "STRESS" in csv_file.name:
                        stress_df = pd.read_csv(csv_file)
                        for row in stress_df.itertuples(index=False):
                            record = self._handle_garmin_stress(user, row)
                            if record:
                                records.append(record)
                    
                    else:
                        self.logger.info(f"Skipping unrecognized file: {csv_file.name}")
                
                except pd.errors.EmptyDataError:
                    self.logger.info(f"Skipping empty CSV file: {csv_file.name}")
                except Exception as e:
                    self.logger.error(f"Error reading {csv_file.name}: {e}")
            
            # Group records by collection and insert into MongoDB
            self.logger.info(f"Total records created: {len(records)}")
            collections_records = {}
            for record in records:
                if record:
                    collection_name = record[0]
                    record_data = record[1]
                    if collection_name in collections_records:
                        collections_records[collection_name].append(record_data)
                    else:
                        collections_records[collection_name] = [record_data]
            
            self.logger.info(f"Records grouped by collection: {list(collections_records.keys())}")
            for collection_name, record_list in collections_records.items():
                self.logger.info(f"  {collection_name}: {len(record_list)} records")
            
            # Insert records into MongoDB
            for collection_name, record_list in collections_records.items():
                if record_list:
                    try:
                        self.db[collection_name].insert_many(record_list, ordered=False)
                        self.logger.info(f"Inserted {len(record_list)} records into {collection_name}")
                    except Exception as e:
                        self.logger.error(f"Error inserting records into {collection_name}: {e}")
            
            # Clean up CSV files
            try:
                import shutil
                shutil.rmtree(csv_directory)
                self.logger.info(f"Cleaned up CSV directory: {csv_directory}")
            except Exception as e:
                self.logger.error(f"Failed to clean up CSV directory {csv_directory}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Exception processing Garmin CSV files: {e}")
            return False
    
    def process_phone_data(self, user: str) -> bool:
        """
        Process phone data for a specific user.
        
        Args:
            user: User ID
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            self.logger.info(f"Processing phone data for user: {user}")
            
            # Load phone data from uploads
            self.logger.info(f"Config data_upload_path: {self.config.paths.data_upload_path}")
            
            upload_path = Path(self.config.paths.data_upload_path) / "phone" / user
            self.logger.info(f"Trying path: {upload_path}")
            if not upload_path.exists():
                self.logger.warning(f"Path does not exist: {upload_path}")
                # Try without phone subdirectory for backward compatibility
                upload_path = Path(self.config.paths.data_upload_path) / user
                self.logger.info(f"Trying fallback path: {upload_path}")
                if not upload_path.exists():
                    self.logger.warning(f"Fallback path also does not exist: {upload_path}")
                    self.logger.warning(f"No upload directory found for user: {user}")
                    self.logger.warning(f"Tried paths: {Path(self.config.paths.data_upload_path) / 'phone' / user} and {Path(self.config.paths.data_upload_path) / user}")
                    return False
            else:
                self.logger.info(f"Found upload directory: {upload_path}")
            
            # Process different types of phone data
            self._process_location_data(user, upload_path)
            self._process_sensor_data(user, upload_path)
            
            # Flush any remaining records
            self.flush_records()
            
            self.logger.info(f"Successfully processed phone data for user: {user}")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception processing phone data for {user}: {e}")
            return False
    
    def process_garmin_data(self, user: str) -> bool:
        """
        Process Garmin data for a specific user.
        
        Args:
            user: User ID
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            self.logger.info(f"Processing Garmin data for user: {user}")
            
            # Look for FIT files in the same directory structure as phone data
            upload_path = Path(self.config.paths.data_upload_path) / "phone" / user
            self.logger.info(f"Checking for Garmin files in: {upload_path}")
            
            if not upload_path.exists():
                self.logger.info(f"Primary path does not exist: {upload_path}")
                # Try without phone subdirectory for backward compatibility
                upload_path = Path(self.config.paths.data_upload_path) / user
                self.logger.info(f"Checking fallback path: {upload_path}")
                if not upload_path.exists():
                    self.logger.warning(f"No upload directory found for user: {user}")
                    return False
            else:
                self.logger.info(f"Found upload directory: {upload_path}")
            
            # Find all FIT files for this user
            fit_files = list(upload_path.glob("*.fit"))
            self.logger.info(f"Found {len(fit_files)} FIT files in {upload_path}")
            
            if not fit_files:
                self.logger.info(f"No FIT files found for user: {user}")
                return True  # Not an error if no files exist
            
            processed_count = 0
            for fit_file in fit_files:
                try:
                    self.logger.info(f"Processing Garmin FIT file: {fit_file}")
                    success = self.process_garmin_fit_file(user, str(fit_file))
                    if success:
                        processed_count += 1
                        # Archive the processed file
                        self.archive_file(user, str(fit_file))
                except Exception as e:
                    self.logger.error(f"Error processing FIT file {fit_file}: {e}")
                    continue
            
            self.logger.info(f"Successfully processed {processed_count} Garmin files for user: {user}")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception processing Garmin data for {user}: {e}")
            return False
    
    def _process_location_data(self, user: str, upload_path: Path):
        """Process location/GPS data from iOS database files."""
        # Location data is now processed as part of sensor data from iOS databases
        # This method is kept for backward compatibility but location processing
        # is handled in _process_sensor_data when processing iOS .db files
        self.logger.info(f"Location data processing is handled in sensor data processing for user: {user}")
    
    def _process_sensor_data(self, user: str, upload_path: Path):
        """Process iOS sensor data from SQLite database files."""
        # Look for iOS database files (.db files)
        db_files = list(upload_path.glob("*.db"))
        
        for file_path in db_files:
            try:
                self.logger.info(f"Processing iOS database file: {file_path}")
                self._process_ios_database(user, file_path)
                
            except Exception as e:
                self.logger.error(f"Error processing iOS database file {file_path}: {e}")
    
    def _process_ios_database(self, user: str, db_file: Path):
        """Process iOS SQLite database file containing sensor data."""
        try:
            import sqlite3
            
            # Connect to the SQLite database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Get all tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                self.logger.info(f"Processing table: {table_name}")
                
                # Get all records from the table
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                for row in rows:
                    try:
                        # Process based on event_id (row[3])
                        if len(row) >= 4:
                            event_id = row[3]
                            self._process_event_by_id(user, row, event_id)
                            
                    except Exception as e:
                        self.logger.error(f"Error processing row in table {table_name}: {e}")
                        continue
            
            conn.close()
            
            # Archive the processed file
            self.archive_file(user, str(db_file))
            
            self.logger.info(f"Successfully processed iOS database: {db_file}")
            
        except Exception as e:
            self.logger.error(f"Error processing iOS database {db_file}: {e}")
    
    def _process_event_by_id(self, user: str, row, event_id):
        """Process event based on event_id."""
        try:
            # Core sensor events
            if event_id in [152, 151]:  # Location events
                self._process_location_record(user, row)
            elif event_id == 16:  # Activity events
                self._process_activity_record(user, row)
            elif event_id == 21:  # Steps events
                self._process_steps_record(user, row)
            elif event_id in [11, 111]:  # Battery events
                self._process_battery_record(user, row)
            elif event_id in [18, 181]:  # WiFi events
                self._process_wifi_record(user, row)
            elif event_id == 19:  # Bluetooth events
                self._process_bluetooth_record(user, row)
            elif event_id == 13:  # Brightness events
                self._process_brightness_record(user, row)
            elif event_id == 14:  # Lock/Unlock events
                self._process_lock_unlock_record(user, row)
            elif event_id == 447:  # Accelerometer events
                self._process_accelerometer_record(user, row)
            elif event_id == 23:  # Call log events
                self._process_calllog_record(user, row)
            elif event_id == 442:  # Garmin heart rate events
                self._process_garmin_hr_record(user, row)
            elif event_id == 443:  # Garmin stress events
                self._process_garmin_stress_record(user, row)
            elif event_id == 501:  # App usage events
                self._process_app_usage_record(user, row)
            elif event_id == 502:  # EMA response events
                self._process_ema_response_record(user, row)
            elif event_id == 503:  # EMA status events
                self._process_ema_status_record(user, row)
            elif event_id == 504:  # Notification events
                self._process_notification_record(user, row)
            else:
                # Unknown event_id - store in generic collection
                self._process_unknown_event_record(user, row, event_id)
                
        except Exception as e:
            self.logger.error(f"Error processing event_id {event_id}: {e}")
    
    def _process_location_record(self, user: str, row):
        """Process location record from iOS database."""
        try:
            # Row structure: [uuid1, uuid2, timestamp, event_id, event_data]
            if len(row) >= 5:
                timestamp = self._handle_timestamp_format(row[2])
                event_id = row[3]
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': event_id,
                    'latitude': float(event_data.get('latitude', 0)),
                    'longitude': float(event_data.get('longitude', 0)),
                    'accuracy': float(event_data.get('accuracy', 0)),
                    'altitude': float(event_data.get('altitude', 0)),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.IOS_LOCATION, record)
                
        except Exception as e:
            self.logger.error(f"Error processing location record: {e}")
    
    def _process_activity_record(self, user: str, row):
        """Process activity record from iOS database."""
        try:
            if len(row) >= 4:
                timestamp = self._handle_timestamp_format(row[2])
                event_data = row[4].decode("utf-8") if isinstance(row[4], bytes) else str(row[4])
                
                # Parse activity data (format: "activity1 activity2,confidence")
                split_event = event_data.split(',')
                activities = split_event[0].split(' ')[:-1] if len(split_event) > 0 else []
                confidence = split_event[1] if len(split_event) > 1 else 0
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': row[3],
                    'activity': activities,
                    'confidence': confidence,
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.IOS_ACTIVITY, record)
                
        except Exception as e:
            self.logger.error(f"Error processing activity record: {e}")
    
    def _process_steps_record(self, user: str, row):
        """Process steps record from iOS database."""
        try:
            if len(row) >= 4:
                start_timestamp = self._handle_timestamp_format(row[2])
                event_data = row[4].decode("utf-8") if isinstance(row[4], bytes) else str(row[4])
                
                # Parse steps data (format: "end_timestamp,steps,distance,floors_ascended,floors_descended")
                split_event = event_data.split(',')
                
                record = {
                    'uid': user,
                    'start_timestamp': start_timestamp,
                    'event_id': row[3],
                    'end_timestamp': self._handle_timestamp_format(split_event[0]) if len(split_event) > 0 else start_timestamp,
                    'steps': int(split_event[1]) if len(split_event) > 1 else 0,
                    'distance': float(split_event[2]) if len(split_event) > 2 else 0,
                    'floors_ascended': float(split_event[3]) if len(split_event) > 3 else 0,
                    'floors_descended': float(split_event[4]) if len(split_event) > 4 else 0,
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.IOS_STEPS, record)
                
        except Exception as e:
            self.logger.error(f"Error processing steps record: {e}")
    
    def _process_battery_record(self, user: str, row):
        """Process battery record from iOS database."""
        try:
            # Row structure: [uuid1, uuid2, timestamp, event_id, event_data]
            if len(row) >= 5:
                timestamp = self._handle_timestamp_format(row[2])
                event_id = row[3]
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': event_id,
                    'processed_at': datetime.now().timestamp()
                }
                
                # Add battery fields if they exist
                if 'battery_left' in event_data:
                    record['battery_left'] = int(event_data.get('battery_left', 0))
                if 'battery_state' in event_data:
                    record['battery_state'] = int(event_data.get('battery_state', 0))
                
                self.add_record(self.config.collections.IOS_BATTERY, record)
                
        except Exception as e:
            self.logger.error(f"Error processing battery record: {e}")
    
    def _process_wifi_record(self, user: str, row):
        """Process WiFi record from iOS database."""
        try:
            if len(row) >= 5:
                timestamp = self._handle_timestamp_format(row[2])
                event_id = row[3]
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': event_id,
                    'processed_at': datetime.now().timestamp()
                }
                
                # Handle different WiFi event types
                if event_id == 18:
                    record['bssid'] = event_data.get('bssid', '')
                    record['ssid'] = event_data.get('ssid', '')
                elif event_id == 181:
                    record['wifi_enabled'] = int(event_data.get('wifi_enabled', 0))
                    if 'wifi_connected' in event_data:
                        record['wifi_connected'] = int(event_data.get('wifi_connected', 0))
                
                self.add_record(self.config.collections.IOS_WIFI, record)
                
        except Exception as e:
            self.logger.error(f"Error processing WiFi record: {e}")
    
    def _process_bluetooth_record(self, user: str, row):
        """Process Bluetooth record from iOS database."""
        try:
            if len(row) >= 4:
                timestamp = self._handle_timestamp_format(row[2])
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': row[3],
                    'bt_address': event_data.get('bt_address', ''),
                    'bt_rssi': int(event_data.get('bt_rssi', 0)),
                    'bt_name': event_data.get('bt_name', ''),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.IOS_BLUETOOTH, record)
                
        except Exception as e:
            self.logger.error(f"Error processing Bluetooth record: {e}")
    
    def _process_brightness_record(self, user: str, row):
        """Process brightness record from iOS database."""
        try:
            # Row structure: [uuid1, uuid2, timestamp, event_id, event_data]
            if len(row) >= 5:
                timestamp = self._handle_timestamp_format(row[2])
                event_id = row[3]
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': event_id,
                    'brightness': float(event_data.get('brightness', 0)),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.IOS_BRIGHTNESS, record)
                
        except Exception as e:
            self.logger.error(f"Error processing brightness record: {e}")
    
    def _process_lock_unlock_record(self, user: str, row):
        """Process lock/unlock record from iOS database."""
        try:
            # Row structure: [uuid1, uuid2, timestamp, event_id, event_data]
            if len(row) >= 5:
                timestamp = self._handle_timestamp_format(row[2])
                event_id = row[3]
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': event_id,
                    'lock_state': int(event_data.get('LockState', 0)),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.IOS_LOCK_UNLOCK, record)
                
        except Exception as e:
            self.logger.error(f"Error processing lock/unlock record: {e}")
    
    def _process_accelerometer_record(self, user: str, row):
        """Process accelerometer record from iOS database."""
        try:
            if len(row) >= 4:
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': self._handle_timestamp_format(event_data.get('timestamp', row[2])),
                    'event_id': row[2],
                    'x': float(event_data.get('x', 0)),
                    'y': float(event_data.get('y', 0)),
                    'z': float(event_data.get('z', 0)),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.IOS_ACCELEROMETER, record)
                
        except Exception as e:
            self.logger.error(f"Error processing accelerometer record: {e}")
    
    def _process_calllog_record(self, user: str, row):
        """Process call log record from iOS database."""
        try:
            if len(row) >= 4:
                timestamp = self._handle_timestamp_format(row[2])
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': row[2],
                    'call_timestamp': self._handle_timestamp_format(event_data.get('timestamp', 0)),
                    'callId': str(event_data.get('callId', '')),
                    'callType': str(event_data.get('callType', '')),
                    'duration': float(event_data.get('duration', 0)),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.IOS_CALLLOG, record)
                
        except Exception as e:
            self.logger.error(f"Error processing call log record: {e}")
    
    def _process_garmin_hr_record(self, user: str, row):
        """Process Garmin heart rate record from iOS database."""
        try:
            if len(row) >= 4:
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': self._handle_timestamp_format(event_data.get('timestamp', row[2])),
                    'event_id': row[2],
                    'heart_rate': float(event_data.get('heart_rate', 0)),
                    'status': str(event_data.get('status', '')),
                    'device': str(event_data.get('device', '')),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.GARMIN_HR, record)
                
        except Exception as e:
            self.logger.error(f"Error processing Garmin HR record: {e}")
    
    def _process_garmin_stress_record(self, user: str, row):
        """Process Garmin stress record from iOS database."""
        try:
            if len(row) >= 4:
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': self._handle_timestamp_format(event_data.get('timestamp', row[2])),
                    'event_id': row[2],
                    'stress': float(event_data.get('stress', 0)),
                    'status': str(event_data.get('status', '')),
                    'device': str(event_data.get('device', '')),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.GARMIN_STRESS, record)
                
        except Exception as e:
            self.logger.error(f"Error processing Garmin stress record: {e}")
    
    def _process_app_usage_record(self, user: str, row):
        """Process app usage record from iOS database."""
        try:
            if len(row) >= 4:
                timestamp = self._handle_timestamp_format(row[2])
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': row[2],
                    'appName': str(event_data.get('appName', '')),
                    'status': str(event_data.get('status', '')),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.APP_USAGE_LOGS, record)
                
        except Exception as e:
            self.logger.error(f"Error processing app usage record: {e}")
    
    def _process_ema_response_record(self, user: str, row):
        """Process EMA response record from iOS database."""
        try:
            if len(row) >= 4:
                timestamp = self._handle_timestamp_format(row[2])
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': row[2],
                    'ema_id': str(event_data.get('ema_id', '')),
                    'questions': event_data.get('questions', {}),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.EMA_RESPONSE, record)
                
        except Exception as e:
            self.logger.error(f"Error processing EMA response record: {e}")
    
    def _process_ema_status_record(self, user: str, row):
        """Process EMA status record from iOS database."""
        try:
            if len(row) >= 4:
                timestamp = self._handle_timestamp_format(row[2])
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': row[2],
                    'ema_id': str(event_data.get('ema_id', '')),
                    'status': str(event_data.get('status', '')),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.EMA_STATUS_EVENTS, record)
                
        except Exception as e:
            self.logger.error(f"Error processing EMA status record: {e}")
    
    def _process_notification_record(self, user: str, row):
        """Process notification record from iOS database."""
        try:
            if len(row) >= 4:
                timestamp = self._handle_timestamp_format(row[2])
                event_data = json.loads(row[4].decode("utf-8")) if isinstance(row[4], bytes) else row[4]
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': row[2],
                    'notification_id': str(event_data.get('notification_id', '')),
                    'status': str(event_data.get('status', '')),
                    'expectedScheduledTime': event_data.get('expectedScheduledTime', ''),
                    'type': event_data.get('type', ''),
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.NOTIFICATION_EVENTS, record)
                
        except Exception as e:
            self.logger.error(f"Error processing notification record: {e}")
    
    def _process_unknown_event_record(self, user: str, row, event_id):
        """Process unknown event record from iOS database."""
        try:
            # Row structure: [uuid1, uuid2, timestamp, event_id, event_data]
            if len(row) >= 5:
                timestamp = self._handle_timestamp_format(row[2])
                
                record = {
                    'uid': user,
                    'timestamp': timestamp,
                    'event_id': event_id,
                    'raw_data': str(row[4]) if len(row) > 4 else '',
                    'processed_at': datetime.now().timestamp()
                }
                
                self.add_record(self.config.collections.UNKNOWN_EVENTS, record)
                
        except Exception as e:
            self.logger.error(f"Error processing unknown event record: {e}")
    
    def _handle_timestamp_format(self, timestamp):
        """Handle different timestamp formats."""
        str_time = str(timestamp)
        if len(str_time.split(".")[0]) == 10:
            return float(timestamp)
        else:
            return float(timestamp) / 1000
    
    # Garmin data handling methods
    def _handle_garmin_accelerometer(self, user: str, row):
        """Handle Garmin accelerometer data."""
        try:
            record = {
                'uid': user,
                'x': row.x,
                'y': row.y,
                'z': row.z,
                'event_id': 447,
                'timestamp': row.timestamp + row.micros / 1_000_000,
                'processed_at': datetime.now().timestamp()
            }
            return 'accelerometer_data', record
        except Exception as e:
            self.logger.error(f"Error processing Garmin accelerometer: {e}")
            return None
    
    def _handle_garmin_ibi(self, user: str, row):
        """Handle Garmin IBI (Inter-Beat Interval) data."""
        try:
            record = {
                'uid': user,
                'timestamp': row.timestamp + row.millis / 1_000,
                'bbi': row.bbi,
                'event_id': 441,
                'processed_at': datetime.now().timestamp()
            }
            return self.config.collections.GARMIN_IBI, record
        except Exception as e:
            self.logger.error(f"Error processing Garmin IBI: {e}")
            return None
    
    def _handle_garmin_hr(self, user: str, row):
        """Handle Garmin heart rate data."""
        try:
            record = {
                'uid': user,
                'event_id': 442,
                'timestamp': row.timestamp,
                'heart_rate': float(row.bpm),
                'status': str(row.status),
                'processed_at': datetime.now().timestamp()
            }
            return self.config.collections.GARMIN_HR, record
        except Exception as e:
            self.logger.error(f"Error processing Garmin heart rate: {e}")
            return None
    
    def _handle_garmin_respiration(self, user: str, row):
        """Handle Garmin respiration data."""
        try:
            record = {
                'uid': user,
                'event_id': 444,
                'respiration_timestamp': row.timestamp,
                'respiration': float(row.breathsPerMinute),
                'status': str(row.respirationStatus),
                'timestamp': row.timestamp,
                'processed_at': datetime.now().timestamp()
            }
            return self.config.collections.GARMIN_RESPIRATION, record
        except Exception as e:
            self.logger.error(f"Error processing Garmin respiration: {e}")
            return None
    
    def _handle_garmin_steps(self, user: str, row):
        """Handle Garmin steps data."""
        try:
            record = {
                'uid': user,
                'event_id': 445,
                'timestamp': row.startTimestamp,
                'start_timestamp': row.startTimestamp,
                'steps_timestamp': row.endTimestamp,
                'steps': float(row.stepCount),
                'total_steps': float(row.totalSteps),
                'processed_at': datetime.now().timestamp()
            }
            return self.config.collections.GARMIN_STEPS, record
        except Exception as e:
            self.logger.error(f"Error processing Garmin steps: {e}")
            return None
    
    def _handle_garmin_stress(self, user: str, row):
        """Handle Garmin stress data."""
        try:
            record = {
                'uid': user,
                'event_id': 443,
                'timestamp': row.timestamp,
                'heart_rate': float(row.stressScore),
                'status': str(row.stressStatus),
                'average_stress_intensity': float(row.averageStressIntensity),
                'body_battery': float(row.bodyBattery),
                'body_battery_status': str(row.bodyBatteryStatus),
                'processed_at': datetime.now().timestamp()
            }
            return self.config.collections.GARMIN_STRESS, record
        except Exception as e:
            self.logger.error(f"Error processing Garmin stress: {e}")
            return None
    

    
    def generate_daily_summaries(self, date: Optional[str] = None, hours_back: int = 2) -> bool:
        """
        Generate daily summaries for all users or a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to last 2 hours for cron jobs)
            hours_back: Number of hours to look back (default: 2 for cron jobs)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if date is None:
                # For cron jobs, process the last 2 hours of data
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=hours_back)
                start_timestamp = int(start_time.timestamp())
                end_timestamp = int(end_time.timestamp())
                target_date = start_time.date()
            else:
                # For manual runs, process the entire day
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
                start_timestamp = int(datetime.combine(target_date, datetime.min.time()).timestamp())
                end_timestamp = int(datetime.combine(target_date, datetime.max.time()).timestamp())
            
            self.logger.info(f"Generating summaries for {target_date} (from {start_timestamp} to {end_timestamp})")
            
            # Get all users
            users = self.db['users'].find({}, {'uid': 1})
            
            for user_doc in users:
                uid = user_doc['uid']
                self._generate_user_daily_summary(uid, start_timestamp, end_timestamp, target_date)
            
            self.logger.info(f"Successfully generated summaries for {target_date}")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception generating daily summaries: {e}")
            return False
    
    def _generate_user_daily_summary(self, uid: str, start_timestamp: int, 
                                   end_timestamp: int, target_date: datetime.date):
        """Generate daily summary for a specific user."""
        try:
            # Get location data
            location_distance, location_duration = self._get_location_info(uid, start_timestamp, end_timestamp)
            
            # Get Garmin data
            garmin_wear_duration, garmin_on_duration = self._get_garmin_info(uid, start_timestamp, end_timestamp)
            
            # Get EMA data
            ema_info = self._get_ema_info(uid, start_timestamp, end_timestamp)
            
            # Create summary document
            summary = {
                'uid': uid,
                'date': start_timestamp,
                'date_str': target_date.strftime("%Y-%m-%d"),
                'location': {
                    'distance_traveled': location_distance,
                    'duration_hours': location_duration
                },
                'garmin_wear_duration': garmin_wear_duration,
                'garmin_on_duration': garmin_on_duration,
                'ema': ema_info,
                'generated_at': datetime.now().timestamp()
            }
            
            # Save to database (upsert to avoid duplicates)
            self.db[self.config.collections.DAILY_SUMMARY].update_one(
                {'uid': uid, 'date': start_timestamp},
                {'$set': summary},
                upsert=True
            )
            
            self.logger.info(f"Generated daily summary for {uid} on {target_date}")
            
        except Exception as e:
            self.logger.error(f"Error generating daily summary for {uid}: {e}")
    
    def _get_location_info(self, uid: str, start_timestamp: int, end_timestamp: int) -> tuple:
        """Get location information for a user."""
        try:
            # Get GPS records
            gps_records = list(self.db['location_data'].find({
                'uid': uid,
                'timestamp': {'$gte': start_timestamp, '$lt': end_timestamp}
            }).sort('timestamp', 1))
            
            if not gps_records:
                return 0.0, 0.0
            
            # Calculate distance traveled
            distance_traveled = self._calculate_distance_traveled(gps_records)
            
            # Calculate duration
            duration_hours = len(gps_records) * 10 / 3600  # Assuming 10-minute intervals
            
            return distance_traveled, duration_hours
            
        except Exception as e:
            self.logger.error(f"Error getting location info for {uid}: {e}")
            return 0.0, 0.0
    
    def _calculate_distance_traveled(self, gps_records: List[Dict]) -> float:
        """Calculate total distance traveled from GPS records."""
        try:
            if len(gps_records) < 2:
                return 0.0
            
            total_distance = 0.0
            for i in range(1, len(gps_records)):
                prev = gps_records[i-1]
                curr = gps_records[i]
                
                try:
                    dist = distance.distance(
                        (prev.get('latitude', 0), prev.get('longitude', 0)),
                        (curr.get('latitude', 0), curr.get('longitude', 0))
                    ).meters
                    total_distance += dist
                except:
                    continue
            
            return total_distance
            
        except Exception as e:
            self.logger.error(f"Error calculating distance: {e}")
            return 0.0
    
    def _get_garmin_info(self, uid: str, start_timestamp: int, end_timestamp: int) -> tuple:
        """Get Garmin device information for a user."""
        try:
            # Get Garmin heart rate records (indicates device is worn)
            garmin_hr_records = list(self.db['garmin_hr_data'].find({
                'uid': uid,
                'timestamp': {'$gte': start_timestamp, '$lt': end_timestamp}
            }))
            
            # Get Garmin stress records (indicates device is on and monitoring)
            garmin_stress_records = list(self.db['garmin_stress_data'].find({
                'uid': uid,
                'timestamp': {'$gte': start_timestamp, '$lt': end_timestamp}
            }))
            
            # Calculate durations (assuming 6-minute intervals for each record)
            garmin_wear_duration = len(garmin_hr_records) * 6 / 60  # Convert to hours
            garmin_on_duration = len(garmin_stress_records) * 6 / 60  # Convert to hours
            
            return garmin_wear_duration, garmin_on_duration
            
        except Exception as e:
            self.logger.error(f"Error getting Garmin info for {uid}: {e}")
            return 0.0, 0.0
    
    def _get_sensor_info(self, uid: str, start_timestamp: int, end_timestamp: int) -> float:
        """Get sensor information for a user."""
        try:
            # Get various sensor data types
            activity_records = list(self.db['activity_data'].find({
                'uid': uid,
                'timestamp': {'$gte': start_timestamp, '$lt': end_timestamp}
            }))
            
            steps_records = list(self.db['steps_data'].find({
                'uid': uid,
                'start_timestamp': {'$gte': start_timestamp, '$lt': end_timestamp}
            }))
            
            battery_records = list(self.db['battery_data'].find({
                'uid': uid,
                'timestamp': {'$gte': start_timestamp, '$lt': end_timestamp}
            }))
            
            # Calculate total sensor activity duration
            # This is a simplified calculation - in practice you might want more sophisticated logic
            total_records = len(activity_records) + len(steps_records) + len(battery_records)
            
            # Assume each record represents some time period (e.g., 1 minute)
            total_duration_minutes = total_records
            
            return total_duration_minutes / 60  # Convert to hours
            
        except Exception as e:
            self.logger.error(f"Error getting sensor info for {uid}: {e}")
            return 0.0
    
    def _get_ema_info(self, uid: str, start_timestamp: int, end_timestamp: int) -> Dict:
        """Get EMA information for a user."""
        try:
            # Get EMA responses
            ema_responses = list(self.db['ema_data'].find({
                'uid': uid,
                'timestamp': {'$gte': start_timestamp, '$lt': end_timestamp}
            }))
            
            # Get scheduled EMAs
            scheduled_emas = list(self.db['ema_schedule'].find({
                'uid': uid,
                'timestamp': {'$gte': start_timestamp, '$lt': end_timestamp}
            }))
            
            return {
                'responses': ema_responses,
                'scheduled': scheduled_emas,
                'response_count': len(ema_responses),
                'scheduled_count': len(scheduled_emas)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting EMA info for {uid}: {e}")
            return {'responses': [], 'scheduled': [], 'response_count': 0, 'scheduled_count': 0}
    

    
    def generate_plots(self, user: str, date: str) -> bool:
        """
        Generate plots for a specific user and date.
        
        Args:
            user: User ID
            date: Date in YYYY-MM-DD format
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Generating plots for {user} on {date}")
            
            # Create plots directory
            plots_dir = Path(self.config.paths.static_dir) / user
            plots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate different types of plots
            self._generate_location_plot(user, date, plots_dir)
            self._generate_sensor_plot(user, date, plots_dir)
            self._generate_ema_plot(user, date, plots_dir)
            
            self.logger.info(f"Successfully generated plots for {user} on {date}")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception generating plots for {user}: {e}")
            return False
    
    def _generate_location_plot(self, user: str, date: str, plots_dir: Path):
        """Generate location plot."""
        try:
            # This would use a plotting library like matplotlib or plotly
            # For now, we'll create a placeholder
            plot_content = f"""
            <html>
            <head><title>Location Data - {user} - {date}</title></head>
            <body>
            <h1>Location Data for {user} on {date}</h1>
            <p>Location visualization would be generated here.</p>
            </body>
            </html>
            """
            
            plot_file = plots_dir / f"{date}.html"
            with open(plot_file, 'w') as f:
                f.write(plot_content)
                
        except Exception as e:
            self.logger.error(f"Error generating location plot for {user}: {e}")
    
    def _generate_sensor_plot(self, user: str, date: str, plots_dir: Path):
        """Generate sensor plot."""
        try:
            plot_content = f"""
            <html>
            <head><title>Sensor Data - {user} - {date}</title></head>
            <body>
            <h1>Sensor Data for {user} on {date}</h1>
            <p>Sensor visualization would be generated here.</p>
            </body>
            </html>
            """
            
            plot_file = plots_dir / "sensor" / f"{date}.html"
            plot_file.parent.mkdir(exist_ok=True)
            with open(plot_file, 'w') as f:
                f.write(plot_content)
                
        except Exception as e:
            self.logger.error(f"Error generating sensor plot for {user}: {e}")
    
    def _generate_ema_plot(self, user: str, date: str, plots_dir: Path):
        """Generate EMA plot."""
        try:
            plot_content = f"""
            <html>
            <head><title>EMA Data - {user} - {date}</title></head>
            <body>
            <h1>EMA Data for {user} on {date}</h1>
            <p>EMA visualization would be generated here.</p>
            </body>
            </html>
            """
            
            plot_file = plots_dir / "ema" / f"{date}.html"
            plot_file.parent.mkdir(exist_ok=True)
            with open(plot_file, 'w') as f:
                f.write(plot_content)
                
        except Exception as e:
            self.logger.error(f"Error generating EMA plot for {user}: {e}")
    



def process_all_data():
    """Process all data for all users."""
    processor = DataProcessor()
    
    # Get all users
    users = processor.db['users'].find({}, {'uid': 1})
    
    for user_doc in users:
        uid = user_doc['uid']
        # Process phone data
        processor.process_phone_data(uid)
        # Process Garmin data
        processor.process_garmin_data(uid)
    
    # Generate daily summaries
    processor.generate_daily_summaries()


def generate_all_summaries():
    """Generate daily summaries for all users."""
    processor = DataProcessor()
    processor.generate_daily_summaries()


def process_garmin_files():
    """Process all Garmin FIT files."""
    # Set the STUDY_CONFIG_FILE environment variable if not already set
    if 'STUDY_CONFIG_FILE' not in os.environ:
        # Try to find the config file in common locations
        from pathlib import Path
        
        # Look for config file in current directory or parent directories
        current_dir = Path.cwd()
        config_file = None
        
        # Check current directory
        if (current_dir / "config" / "study_config.json").exists():
            config_file = current_dir / "config" / "study_config.json"
        # Check parent directories
        else:
            for parent in current_dir.parents:
                if (parent / "config" / "study_config.json").exists():
                    config_file = parent / "config" / "study_config.json"
                    break
        
        if config_file:
            os.environ['STUDY_CONFIG_FILE'] = str(config_file)
            print(f"Set STUDY_CONFIG_FILE to: {config_file}")
            
            # Reload the configuration with the new file
            from study_framework_core.core.config import set_config_file
            set_config_file(str(config_file))
        else:
            print("Warning: Could not find study_config.json. Using default configuration.")
    
    processor = DataProcessor()
    
    # Get all users
    users = processor.db['users'].find({}, {'uid': 1})
    
    for user_doc in users:
        uid = user_doc['uid']
        # Use the proper method that handles archiving and user-specific processing
        processor.process_garmin_data(uid)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Study Framework Data Processing')
    parser.add_argument('--action', choices=['process_data', 'generate_summaries', 'process_garmin'], 
                       required=True, help='Action to perform')
    parser.add_argument('--user', help='Specific user to process')
    parser.add_argument('--date', help='Specific date (YYYY-MM-DD)')
    parser.add_argument('--hours-back', type=int, default=2, help='Hours to look back for summaries (default: 2)')
    
    args = parser.parse_args()
    
    if args.action == 'process_data':
        if args.user:
            processor = DataProcessor()
            processor.process_phone_data(args.user)
        else:
            process_all_data()
    elif args.action == 'generate_summaries':
        if args.date:
            processor = DataProcessor()
            processor.generate_daily_summaries(args.date)
        else:
            processor = DataProcessor()
            processor.generate_daily_summaries(hours_back=args.hours_back)
    elif args.action == 'process_garmin':
        process_garmin_files()
