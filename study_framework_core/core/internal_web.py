"""
Internal web API endpoints for the study framework.
Provides dashboard functionality, user management, and data visualization.
"""

import logging
import os
import json
import time
import io
import csv
import shutil
from datetime import datetime, timedelta
from collections import defaultdict

from flask import Flask, request, jsonify, render_template, Response, send_from_directory, send_file, session, redirect, url_for
from flask_restful import Resource, Api
from markupsafe import Markup

from study_framework_core.core.config import get_config
from study_framework_core.core.handlers import get_db, verify_admin_login, get_available_modules
from study_framework_core.core.dashboard import DashboardBase

# Create a concrete dashboard implementation for internal web
class SimpleDashboard(DashboardBase):
    def _get_custom_columns(self):
        return []
    
    def generate_custom_row_data(self, user_data, date_str):
        return dict()


class HealthCheck(Resource):
    """Health check endpoint for internal web."""
    def get(self):
        return {'status': 'healthy', 'service': 'study-framework-internal'}, 200


class InternalWebBase:
    """Base class for internal web functionality."""
    
    def __init__(self, app: Flask, dashboard: DashboardBase):
        self.app = app
        self.dashboard = dashboard
        self.api = Api(app, prefix='/internal_web')
        self.setup_routes()
        self.setup_session_config()
    
    def setup_session_config(self):
        """Setup session configuration."""
        self.app.secret_key = os.urandom(24)  # Generate a random secret key
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)  # Session lasts 15 minutes
        self.app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for development
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    def setup_routes(self):
        """Setup internal web routes."""
        # Health check route
        self.api.add_resource(HealthCheck, '/health')
        
        # Authentication routes
        self.api.add_resource(LoginPage, '/login')
        self.api.add_resource(LoginHandler, '/login-handler')
        self.api.add_resource(LogoutHandler, '/logout')
        self.api.add_resource(LandingPage, '/')
        
        # Dashboard routes (now require authentication)
        self.api.add_resource(ViewDashboard, '/dashboard')
        self.api.add_resource(ViewDashboardDate, '/dashboard/<date>')
        self.api.add_resource(ViewUserDetail, '/dashboard/view/<user>/<date>')
        self.api.add_resource(ViewUserEma, '/dashboard/ema/<user>/<date>')
        self.api.add_resource(ViewUserAppUsage, '/dashboard/app-usage/<user>/<date>')
        self.api.add_resource(ViewAnnouncement, '/dashboard/announcement')
        
        # Data download routes
        self.api.add_resource(DownloadCompliance, '/download_compliance')
        self.api.add_resource(DownloadEmaAll, '/download_ema_all')
        
        # EMA Schedule routes
        self.api.add_resource(Users, '/ema-schedule/users')
        self.api.add_resource(ReplaceEMA, '/ema-schedule/replace-ema')
        self.api.add_resource(AddUserFile, '/ema-schedule/add-user')
        self.api.add_resource(DownloadUserFile, '/ema-schedule/download/<string:user>')
        self.api.add_resource(EmaFrontend, '/ema-schedule')
        self.api.add_resource(ConfigFrontend, '/config-schedule')
        
        # User Management Routes
        self.api.add_resource(UserManagementFrontend, '/user-management')
        self.api.add_resource(CreateSingleUser, '/user-management/create-single')
        self.api.add_resource(CreateMultipleUsers, '/user-management/create-multiple')
        self.api.add_resource(GetUsers, '/user-management/users')
        self.api.add_resource(ExportUsers, '/user-management/export')


def handle_response(message, status):
    """Create standardized response."""
    return {'message': message, "status": status}


def require_auth(f):
    """Decorator to require authentication for internal web endpoints."""
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        return f(*args, **kwargs)
    return decorated_function


class LoginPage(Resource):
    """Login page for internal web access."""
    def get(self):
        if 'admin_logged_in' in session:
            return redirect('/internal_web/')
        
        return Response(
            render_template('login.html'),
            mimetype='text/html'
        )


class LoginHandler(Resource):
    """Handle login form submission."""
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return {'success': False, 'error': 'Username and password are required'}, 400
            
            # Verify credentials
            result = verify_admin_login(username, password)
            
            if result['success']:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                session.permanent = True  # Make session permanent
                logging.info(f"Login successful for {username}, session: {dict(session)}")
                return {'success': True, 'redirect': '/internal_web/'}, 200
            else:
                return {'success': False, 'error': result['error']}, 401
                
        except Exception as e:
            logging.error(f"Login error: {e}")
            return {'success': False, 'error': 'Login failed'}, 500


class LogoutHandler(Resource):
    """Handle logout."""
    def get(self):
        session.clear()
        return redirect('/internal_web/login')


class LandingPage(Resource):
    """Landing page showing all available modules."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        modules = get_available_modules()
        
        return Response(
            render_template('landing_page.html', modules=modules, username=session.get('admin_username')),
            mimetype='text/html'
        )


class ViewDashboard(Resource):
    """View dashboard for a specific date."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        logging.info(f"ViewDashboard accessed by {session.get('admin_username')}")
        
        # Get yesterday's date as default
        today_date = datetime.now().date() - timedelta(days=1)
        date_str = today_date.strftime("%m-%d-%y")
        
        # Get users from database
        db = get_db()
        users = list(db['users'].find())
        users.append({'uid': 'varunm'})  # Add test user
        
        # Generate dashboard context
        dashboard = SimpleDashboard()
        context = dashboard.get_template_context(None, date_str, users)  # No token needed
        
        return Response(
            render_template('dashboard_base.html', **context),
            mimetype='text/html'
        )


class ViewDashboardDate(Resource):
    """View dashboard for a specific date."""
    def get(self, date):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        logging.info(f"ViewDashboardDate accessed by {session.get('admin_username')}, date: {date}")
        
        try:
            # Parse date
            request_date = datetime.strptime(date, "%m-%d-%y").date()
            date_str = request_date.strftime("%m-%d-%y")
            
            # Get users from database
            db = get_db()
            users = list(db['users'].find())
            users.append({'uid': 'varunm'})  # Add test user
            
            # Generate dashboard context
            dashboard = SimpleDashboard()
            context = dashboard.get_template_context(None, date_str, users)  # No token needed
            
            return Response(
                render_template('dashboard_base.html', **context),
                mimetype='text/html'
            )
            
        except ValueError as e:
            logging.error(f"Error parsing date: {e}")
            return {"message": "Bad request", "status": 400}, 400


class ViewUserDetail(Resource):
    """View detailed user information."""
    def get(self, user, date):
        logging.info(f"ViewUserDetail accessed - Session: {dict(session)}")
        if 'admin_logged_in' not in session:
            logging.warning(f"User not logged in, redirecting to login. Session keys: {list(session.keys())}")
            return redirect('/internal_web/login')
        
        config = get_config()
        
        try:
            current_date = datetime.strptime(date, "%m-%d-%y")
            previous_date = (current_date - timedelta(days=1)).strftime("%m-%d-%y")
            next_date = (current_date + timedelta(days=1)).strftime("%m-%d-%y")
            
            # Look for user detail plot
            plot_path = os.path.join(config.paths.static_dir, user, f"{date}.html")
            
            if os.path.exists(plot_path):
                with open(plot_path, 'r') as file:
                    plot_content = file.read()
                return Response(
                    render_template('user_detail.html', 
                                  user=user, date=date,
                                  plot_content=Markup(plot_content), 
                                  previous_date=previous_date,
                                  next_date=next_date), 
                    mimetype='text/html'
                )
            else:
                return {"message": "Plot not found", "status": 404}, 404
                
        except ValueError as e:
            return {"message": "Invalid date format", "status": 400}, 400


class ViewUserEma(Resource):
    """View user EMA information."""
    def get(self, user, date):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        config = get_config()
        
        try:
            current_date = datetime.strptime(date, "%m-%d-%y")
            previous_date = (current_date - timedelta(days=1)).strftime("%m-%d-%y")
            next_date = (current_date + timedelta(days=1)).strftime("%m-%d-%y")
            
            # Get EMA data from database
            db = get_db()
            config = get_config()
            date_timestamp = int(datetime.strptime(date, "%m-%d-%y").timestamp())
            daily_summary = db[config.collections.DAILY_SUMMARY].find_one({'uid': user, "date": date_timestamp})
            
            completed_emas = []
            if daily_summary and 'completed_emas' in daily_summary:
                completed_emas = daily_summary['completed_emas']
            
            # Look for EMA plot
            plot_path = os.path.join(config.paths.static_dir, user, 'ema', f"{date}.html")
            
            if os.path.exists(plot_path):
                with open(plot_path, 'r') as file:
                    plot_content = file.read()
                return Response(
                    render_template('user_ema.html', 
                                  user=user, date=date,
                                  plot_content=Markup(plot_content), 
                                  previous_date=previous_date,
                                  next_date=next_date,
                                  ema=completed_emas), 
                    mimetype='text/html'
                )
            else:
                return {"message": "Plot not found", "status": 404}, 404
                
        except ValueError as e:
            return {"message": "Invalid date format", "status": 400}, 400


class ViewUserAppUsage(Resource):
    """View user app usage information."""
    def get(self, user, date):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        config = get_config()
        
        try:
            current_date = datetime.strptime(date, '%m-%d-%y')
            prev_date = (current_date - timedelta(days=1)).strftime('%m-%d-%y')
            next_date = (current_date + timedelta(days=1)).strftime('%m-%d-%y')
            
            # Get app usage data from database
            db = get_db()
            config = get_config()
            date_timestamp = int(datetime.strptime(date, "%m-%d-%y").timestamp())
            daily_summary = db[config.collections.DAILY_SUMMARY].find_one({'uid': user, "date": date_timestamp})
            
            app_info = {}
            if daily_summary and 'app_events_info' in daily_summary:
                app_info = daily_summary['app_events_info']
            
            # Look for app usage plot
            plot_path = os.path.join(config.paths.static_dir, user, 'app_events', f"{date}.html")
            
            if os.path.exists(plot_path):
                with open(plot_path, 'r') as file:
                    plot_content = file.read()
                template = render_template('user_app_usage.html', 
                                         user=user, date=date,
                                         plot_content=Markup(plot_content),
                                         app_info=app_info, 
                                         previous_date=prev_date, 
                                         next_date=next_date)
            else:
                template = render_template('user_app_usage.html', 
                                         user=user, date=date,
                                         plot_content="",
                                         app_info=app_info, 
                                         previous_date=prev_date, 
                                         next_date=next_date)
            
            return Response(template, mimetype='text/html')
            
        except ValueError as e:
            return {"message": "Invalid date format", "status": 400}, 400


class ViewAnnouncement(Resource):
    """View and manage announcements."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        logging.info(f"ViewAnnouncement accessed by {session.get('admin_username')}")
        
        # Get users from database
        db = get_db()
        users = db['users'].find()
        
        template = render_template("user_announcement.html", token=token, users=users)
        return Response(template, mimetype="text/html")
    
    def post(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        logging.info(f"ViewAnnouncement accessed using post by {session.get('admin_username')}")
        
        config = get_config()
        data = request.json
        if data['pass_key'] == config.security.announcement_pass_key:
            selected_users = data['selected_users']
            announcement = data['announcement']
            alert_message = data['alert_message']
            debug_device = data.get('debug_device', False)
            
            # Get users from database
            db = get_db()
            users_collection = db['users']
            
            response_data = {}
            for user_uid in selected_users:
                user_info = users_collection.find_one({"uid": user_uid})
                if user_info:
                    push_token = user_info.get('push_token', '')
                    try:
                        # Generate announcement (placeholder)
                        logging.info(f"Generated announcement for user {user_uid}: {alert_message}")
                        response_data[user_uid] = "success"
                    except Exception as e:
                        logging.error(f"Failed to generate announcement for user {user_uid}: {e}")
                        response_data[user_uid] = "failure"
            
            return handle_response(response_data, 200), 200
        else:
            return handle_response({"error": "wrong passkey"}, 403), 403


class DownloadCompliance(Resource):
    """Download compliance data as CSV."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        logging.info(f"Accessing Download Page by {session.get('admin_username')}")
        template = render_template("compliance_downloader.html")
        return Response(template, mimetype="text/html")
    
    def post(self):
        logging.info("Accessing Download csv with request")
        data = request.json
        
        start_date = data['start_date']
        end_date = data['end_date']
        type = data['type']
        
        # Get database
        db = get_db()
        
        # Convert date strings to Unix timestamps
        start_time_stamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_time_stamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        
        # Fetch records from MongoDB
        config = get_config()
        records = db[config.collections.DAILY_SUMMARY].find({'date': {'$gte': start_time_stamp, '$lte': end_time_stamp}})
        
        if type == 'aggregation':
            # Aggregate metrics per user
            user_metrics = defaultdict(lambda: {
                'total_distance': 0,
                'total_garmin_on': 0,
                'total_phone_on': 0,
                'total_garmin_worn': 0,
                'total_app_events': 0,
                'total_completed_emas': 0,
                'total_scheduled_emas': 0,
                'sum_depression_scores': 0,
                'total_days': 0
            })
            total_dep_count = 0
            
            for record in records:
                uid = record.get('uid', 'unknown')
                user_metrics[uid]['total_distance'] += record.get('distance', 0)
                user_metrics[uid]['total_garmin_on'] += record.get('garmin_on_duration', 0)
                user_metrics[uid]['total_phone_on'] += record.get('location_duration', 0)
                user_metrics[uid]['total_garmin_worn'] += record.get('garmin_wear_duration', 0)
                user_metrics[uid]['total_completed_emas'] += len(record.get('completed_emas', []))
                user_metrics[uid]['total_scheduled_emas'] += len(record.get('scheduled_emas', []))
                
                values = record.get('depression_scores', {}).values()
                if values:
                    user_metrics[uid]['sum_depression_scores'] += sum([int(v) for v in values])
                    total_dep_count += len(values)
                
                user_metrics[uid]['total_days'] += 1
            
            # Prepare CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'User ID', 'Total Distance', 'Total Garmin On', 'Total Phone On', 'Total Garmin Worn',
                'Total App Events', 'Total Completed EMAs', 'Total Scheduled EMAs', 'Mean Depression Score',
                'Total Days'
            ])
            
            for uid, metrics in user_metrics.items():
                mean_depression_score = (
                    metrics['sum_depression_scores'] / total_dep_count if total_dep_count else 0
                )
                writer.writerow([
                    uid,
                    metrics['total_distance'],
                    metrics['total_garmin_on'],
                    metrics['total_phone_on'],
                    metrics['total_garmin_worn'],
                    metrics['total_app_events'],
                    metrics['total_completed_emas'],
                    metrics['total_scheduled_emas'],
                    round(mean_depression_score, 2),
                    metrics['total_days']
                ])
            
            output.seek(0)
            filename = f"aggregated_compliance_{start_date}_to_{end_date}.csv"
            
            return Response(
                output,
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename={filename}"}
            )
        
        elif type == 'daily':
            # Daily records
            records = db[config.collections.DAILY_SUMMARY].find({'date': {'$gte': start_time_stamp, '$lte': end_time_stamp}}).sort("uid", 1)
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'User ID', 'Date', 'Distance', 'Garmin On', 'Phone On', 'Garmin Worn',
                'App Events', 'Completed EMAs', 'Scheduled EMAs', 'Mean Depression Score'
            ])
            
            for record in records:
                uid = record.get('uid', 'unknown')
                distance = record.get('distance', 0)
                garmin_on = record.get('garmin_on_duration', 0)
                phone_on = record.get('location_duration', 0)
                garmin_worn = record.get('garmin_wear_duration', 0)
                completed_emas = len(record.get('completed_emas', []))
                scheduled_emas = len(record.get('scheduled_emas', []))
                date = datetime.fromtimestamp(record['date']).strftime("%Y-%m-%d")
                
                # Calculate mean depression score
                values = record.get('depression_scores', {}).values()
                if values:
                    val = [int(v) for v in values]
                    depression_scores = sum(val) / len(val)
                else:
                    depression_scores = 0
                
                writer.writerow([
                    uid, date, distance, garmin_on, phone_on, garmin_worn,
                    app_events, completed_emas, scheduled_emas, depression_scores
                ])
            
            output.seek(0)
            filename = f"daily_compliance_{start_date}_to_{end_date}.csv"
            
            return Response(
                output,
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename={filename}"}
            )


class Users(Resource):
    """Get list of users with EMA status."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        config = get_config()
        users = []
        
        for user in os.listdir(config.paths.ema_file_path):
            user_path = os.path.join(config.paths.ema_file_path, user)
            ema_path = os.path.join(user_path, 'ema.json')
            
            if os.path.isdir(user_path):
                try:
                    with open(ema_path, 'r') as f:
                        data = json.load(f)
                        is_active = bool(data)
                except (json.JSONDecodeError, FileNotFoundError):
                    is_active = False
                
                users.append({'name': user, 'status': 'active' if is_active else 'inactive'})
        
        return jsonify(users)


class ReplaceEMA(Resource):
    """Replace EMA file for a user."""
    def post(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        config = get_config()
        user = request.form['user']
        file = request.files['file']
        password = request.form.get('password')
        
        if password != config.security.announcement_pass_key:
            return jsonify({'error': 'Invalid password'}), 403
        
        user_path = os.path.join(config.paths.ema_file_path, user)
        if os.path.exists(user_path):
            file.save(os.path.join(user_path, 'ema.json'))
            return jsonify({'message': 'EMA file replaced successfully!'})
        
        return jsonify({'error': 'User does not exist'}), 404


class AddUser(Resource):
    """Add a new user."""
    def post(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        config = get_config()
        user = request.form['user']
        file = request.files['file']
        password = request.form.get('password')
        
        if password != config.security.announcement_pass_key:
            return jsonify({'error': 'Invalid password'}), 403
        
        user_path = os.path.join(config.paths.ema_file_path, user)
        if not os.path.exists(user_path):
            os.makedirs(user_path)
            file.save(os.path.join(user_path, 'ema.json'))
            return jsonify({'message': 'User added successfully!'})
        
        return jsonify({'error': 'User already exists'}), 400


class DownloadEMA(Resource):
    """Download EMA file for a user."""
    def get(self, user):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        config = get_config()
        user_path = os.path.join(config.paths.ema_file_path, user)
        
        if os.path.exists(user_path):
            return send_from_directory(user_path, 'ema.json', as_attachment=True)
        
        return jsonify({'error': 'User does not exist'}), 404


class EmaFrontend(Resource):
    """EMA schedule frontend."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        template = render_template("ema-schedule.html")
        return Response(template, mimetype="text/html")


class ConfigFrontend(Resource):
    """Config schedule frontend."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        template = render_template("config-schedule.html")
        return Response(template, mimetype="text/html")


class DownloadEmaAll(Resource):
    """Download all EMA data with authentication."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        logging.info(f"Accessing EMA download by {session.get('admin_username')}")
        template = render_template("ema_downloader.html")
        return Response(template, mimetype="text/html")

    def post(self):
        VALID_USERNAME = "connect_ra"
        VALID_PASSWORD = "connect123"
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        daily_diaries = data.get("daily_diary", False)
        start_date_str = data.get("start_date")
        end_date_str = data.get("end_date")

        if username != VALID_USERNAME or password != VALID_PASSWORD:
            logging.warning("Unauthorized access attempt")
            return {"message": "Invalid credentials"}, 401

        # Convert the start and end date from string to datetime objects
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            return {"message": "Invalid date format. Please use YYYY-MM-DD."}, 400

        logging.info(f"Authorized access to EMA data with date range: {start_date} to {end_date}")

        # Get configuration
        config = get_config()
        zip_file_path = os.path.join(config.paths.base_dir, "extras", "secure_data.zip")
        folder_to_zip = config.paths.active_sensing_upload_path

        # Create extras directory if it doesn't exist
        os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)

        if daily_diaries:
            if os.path.exists(zip_file_path):
                os.remove(zip_file_path)

            # Create a temporary directory to store filtered files
            temp_dir = os.path.join(config.paths.base_dir, "extras", "temp_filtered_data")
            os.makedirs(temp_dir, exist_ok=True)

            # Walk through the folder and filter files based on creation date
            for root, dirs, files in os.walk(folder_to_zip):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Get the last modification time of the file
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    # Check if the file's modification time is within the date range
                    if start_date <= file_mod_time <= end_date:
                        # Maintain the folder structure in the temp directory
                        relative_path = os.path.relpath(root, folder_to_zip)
                        destination_path = os.path.join(temp_dir, relative_path)

                        # Ensure the destination path exists before copying
                        os.makedirs(destination_path, exist_ok=True)

                        # Copy the filtered file to the temporary directory
                        shutil.copy2(file_path, destination_path)

            # Create a zip file of the filtered data maintaining folder structure
            shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', temp_dir)

            # Clean up the temporary directory
            shutil.rmtree(temp_dir)
            logging.info(f"Sending diaries along with EMAs")

            return send_file(zip_file_path, as_attachment=True, download_name="secure_data.zip")
        else:
            temp_dir = os.path.join(config.paths.base_dir, "extras", "temp_answers")
            os.makedirs(temp_dir, exist_ok=True)

            # Walk through the main folder and collect 'ema_responses' folders
            for root, dirs, files in os.walk(folder_to_zip):
                if "ema_responses" in dirs:  # Look for the 'ema_responses' folder
                    answers_folder = os.path.join(root, "ema_responses")
                    # Determine the relative path from the base folder to preserve the structure
                    relative_path = os.path.relpath(root, folder_to_zip)
                    destination_path = os.path.join(temp_dir, relative_path, "ema_responses")

                    # Ensure the destination path exists before copying
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                    # Copy the 'ema_responses' folder to the new destination
                    shutil.copytree(answers_folder, destination_path)

            # Create a zip file of the temp directory maintaining folder structure
            shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', temp_dir)

            # Clean up the temporary directory
            shutil.rmtree(temp_dir)
            logging.info(f"Sending only EMAs")
            return send_file(zip_file_path, as_attachment=True, download_name="secure_data.zip")


class UserManagementFrontend(Resource):
    """User management frontend."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        template = render_template("user_management.html")
        return Response(template, mimetype="text/html")


class CreateSingleUser(Resource):
    """Create a single participant."""
    def post(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        try:
            data = request.get_json()
            
            # Validate required fields
            uid = data.get('uid')
            if not uid:
                return {'success': False, 'error': 'UID is required'}, 400
            
            email = data.get('email')
            study_id = data.get('study_id', 'A1')
            
            # Create participant
            from study_framework_core.core.handlers import create_user
            result = create_user(uid, email, study_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            logging.error(f"Error creating single participant: {e}")
            return {'success': False, 'error': str(e)}, 500


class CreateMultipleUsers(Resource):
    """Create multiple participants with sequential IDs."""
    def post(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        try:
            data = request.get_json()
            
            # Validate required fields
            user_prefix = data.get('user_prefix')
            num_users = data.get('num_users')
            
            if not user_prefix or not num_users:
                return {'success': False, 'error': 'User prefix and number of users are required'}, 400
            
            if not isinstance(num_users, int) or num_users <= 0 or num_users > 100:
                return {'success': False, 'error': 'Number of users must be between 1 and 100'}, 400
            
            start_id = data.get('start_id', 1)
            email_base = data.get('email_base')
            study_id = data.get('study_id', 'A1')
            
            # Create multiple participants
            from study_framework_core.core.handlers import create_multiple_users
            result = create_multiple_users(user_prefix, num_users, start_id, email_base, study_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            logging.error(f"Error creating multiple participants: {e}")
            return {'success': False, 'error': str(e)}, 500


class GetUsers(Resource):
    """Get all participants."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        try:
            from study_framework_core.core.handlers import get_all_users
            result = get_all_users()
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            logging.error(f"Error getting participants: {e}")
            return {'success': False, 'error': str(e)}, 500


class ExportUsers(Resource):
    """Export participants to CSV."""
    def get(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        try:
            from study_framework_core.core.handlers import export_users_csv
            result = export_users_csv()
            
            if result['success']:
                return Response(
                    result['csv_content'],
                    mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment;filename={result['filename']}"}
                )
            else:
                return result, 400
                
        except Exception as e:
            logging.error(f"Error exporting participants: {e}")
            return {'success': False, 'error': str(e)}, 500


class ReplaceEMA(Resource):
    """Replace EMA file for a user."""
    def __init__(self, ema_type: str = "ema"):
        self.ema_type = ema_type
        self.config = get_config()
        self.db = get_db()
        
    def post(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        try:
            user = request.form['user']
            file = request.files['file']
            password = request.form.get('password')
            
            # Verify password
            if password != self.config.security.announcement_pass_key:
                return jsonify({'error': 'Invalid password'}), 403
            
            # Determine base directory and file name
            if self.ema_type == "ema":
                base_dir = self.config.paths.ema_file_path
                file_name = 'ema.json'
            else:
                base_dir = self.config.paths.config_dir
                file_name = 'config.json'
            
            # Create user directory if it doesn't exist
            user_path = os.path.join(base_dir, user)
            os.makedirs(user_path, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(user_path, file_name)
            file.save(file_path)
            
            logging.info(f"Replaced {self.ema_type} file for user {user}")
            return jsonify({'message': f'{self.ema_type.upper()} file replaced successfully!'})
            
        except Exception as e:
            logging.error(f"Error replacing {self.ema_type} file: {e}")
            return jsonify({'error': f'Failed to replace {self.ema_type} file'}), 500


class AddUserFile(Resource):
    """Add a new user with EMA or config file."""
    def __init__(self, ema_type: str = "ema"):
        self.ema_type = ema_type
        self.config = get_config()
        self.db = get_db()
        
    def post(self):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        try:
            user = request.form['user']
            file = request.files['file']
            password = request.form.get('password')
            
            # Verify password
            if password != self.config.security.announcement_pass_key:
                return jsonify({'error': 'Invalid password'}), 403
            
            # Determine base directory and file name
            if self.ema_type == "ema":
                base_dir = self.config.paths.ema_file_path
                file_name = 'ema.json'
            else:
                base_dir = self.config.paths.config_dir
                file_name = 'config.json'
            
            # Check if user directory already exists
            user_path = os.path.join(base_dir, user)
            if os.path.exists(user_path):
                return jsonify({'error': 'User already exists'}), 400
            
            # Create user directory and save file
            os.makedirs(user_path, exist_ok=True)
            file_path = os.path.join(user_path, file_name)
            file.save(file_path)
            
            logging.info(f"Added {self.ema_type} file for new user {user}")
            return jsonify({'message': f'User added successfully with {self.ema_type} file!'})
            
        except Exception as e:
            logging.error(f"Error adding user with {self.ema_type} file: {e}")
            return jsonify({'error': f'Failed to add user with {self.ema_type} file'}), 500


class DownloadUserFile(Resource):
    """Download EMA or config file for a user."""
    def __init__(self, ema_type: str = "ema"):
        self.ema_type = ema_type
        self.config = get_config()
        self.db = get_db()
        
    def get(self, user):
        if 'admin_logged_in' not in session:
            return redirect('/internal_web/login')
        
        try:
            # Determine base directory and file name
            if self.ema_type == "ema":
                base_dir = self.config.paths.ema_file_path
                file_name = 'ema.json'
            else:
                base_dir = self.config.paths.config_dir
                file_name = 'config.json'
            
            user_path = os.path.join(base_dir, user)
            file_path = os.path.join(user_path, file_name)
            
            if os.path.exists(file_path):
                return send_from_directory(user_path, file_name, as_attachment=True)
            else:
                return jsonify({'error': 'User file does not exist'}), 404
                
        except Exception as e:
            logging.error(f"Error downloading {self.ema_type} file for user {user}: {e}")
            return jsonify({'error': f'Failed to download {self.ema_type} file'}), 500
