# Study Framework Pipeline Test Scripts

This directory contains test scripts to verify the entire data processing pipeline works correctly.

## Prerequisites

Before running the tests, make sure you have:

1. **Server Running**: The Flask API server should be running and accessible via Nginx
2. **Database Connected**: MongoDB should be running and accessible
3. **Test Data**: Place `test_file.zip` in the same directory as the upload script
4. **Dependencies**: All required Python packages should be installed

## Test Workflow

The testing is now separated into two parts:

### **Step 1: Upload Data (From Local Machine)**
Run the upload script from your local machine to upload test data to the server.

### **Step 2: Process Data (On Server)**
Run the processing script on the server to process the uploaded data.

## Test Scripts

### 1. `upload_test_data.py` - Upload Test Data

This script uploads test data from your local machine to the server:

```bash
python upload_test_data.py --server http://your-server.com --user test130
```

**What it does:**
1. ✅ Unzips `test_file.zip` into `test_data/` directory
2. ✅ Creates test user "test130" on the server
3. ✅ Uploads all data files to API endpoints
4. ✅ Optionally cleans up local test data

**Arguments:**
- `--server`: Server URL (required)
- `--user`: User ID for test data (default: test130)
- `--cleanup`: Automatically cleanup local files after upload

### 2. `process_test_data.py` - Process Uploaded Data

This script processes the uploaded data on the server:

```bash
python process_test_data.py --user test130
```

**What it does:**
1. ✅ Checks if test user exists in database
2. ✅ Verifies uploaded files are present
3. ✅ Processes phone data (iOS database files)
4. ✅ Processes Garmin data (FIT files)
5. ✅ Generates daily summaries
6. ✅ Verifies data appears in database
7. ✅ Optionally cleans up test data

**Arguments:**
- `--user`: User ID to process (default: test130)
- `--cleanup`: Automatically cleanup test data after processing

### 3. `test_pipeline_step_by_step.py` - Interactive Testing

This script allows you to test individual components (legacy, for debugging):

```bash
python test_pipeline_step_by_step.py
```

## Test Data

The `test_file.zip` should contain 12 hours of data for user "test130" including:

- **iOS Database Files** (`.db`): Phone sensor data
- **Garmin FIT Files** (`.fit`): Wearable device data
- **JSON Files** (`.json`): Additional sensor data
- **CSV Files** (`.csv`): Processed data files

## Expected Results

After successful pipeline execution, you should see:

### Database Collections with Data:
- `location_data`: GPS coordinates and location info
- `activity_data`: Physical activity types
- `steps_data`: Step counts and movement
- `battery_data`: Device battery information
- `wifi_data`: WiFi connection details
- `bluetooth_data`: Bluetooth device connections
- `brightness_data`: Screen brightness levels
- `garmin_hr_data`: Heart rate data
- `garmin_stress_data`: Stress level data
- `garmin_steps_data`: Garmin step data
- `daily_summaries`: Aggregated daily data

### Dashboard Data:
- User "test130" appears in the dashboard
- Location duration, Garmin wear/on duration
- Distance traveled, EMA responses
- All data properly formatted and displayed

## Troubleshooting

### Common Issues:

1. **API Server Not Running**
   ```
   ❌ API server is not running
   ```
   **Solution**: Start the Flask API server and ensure Nginx is running

2. **Database Connection Failed**
   ```
   ❌ Database connection failed
   ```
   **Solution**: Check MongoDB is running and connection settings

3. **Test File Not Found**
   ```
   ❌ test_file.zip not found
   ```
   **Solution**: Place test_file.zip in the same directory

4. **Upload Failures**
   ```
   ❌ Upload failed with status 500
   ```
   **Solution**: Check API server logs for specific errors

5. **Processing Failures**
   ```
   ❌ Phone data processing failed
   ```
   **Solution**: Check file formats and processing logs

### Debug Steps:

1. **Use Step-by-Step Script**: Run individual steps to isolate issues
2. **Check Logs**: Look at API server and processing logs
3. **Verify Data**: Use option 8 to check what data is in the database
4. **Test Individual Files**: Upload single files to test specific formats

## Cleanup

Both scripts offer cleanup options:

- **Automatic Cleanup**: Removes test user and all associated data
- **Manual Cleanup**: Option 9 in step-by-step script
- **Keep for Inspection**: Choose not to cleanup to examine results

## Dashboard Access

After successful testing, view the results at:
- **Internal Web**: `http://your-server.com/internal_web/`
- **Dashboard**: Look for user "test130" in the dashboard

## Usage Example

```bash
# Step 1: Upload data from your local machine
python upload_test_data.py --server http://your-server.com --user test130

# Step 2: Process data on the server
python process_test_data.py --user test130

# Step 3: View results in dashboard
# Open http://your-server.com/internal_web/ in your browser
```

## File Structure

```
project_root/
├── test_file.zip              # Test data file
├── upload_test_data.py        # Upload script (run from local machine)
├── process_test_data.py       # Processing script (run on server)
├── test_pipeline_step_by_step.py  # Interactive test (legacy)
├── test_data/                 # Extracted test data (created during upload)
└── TEST_README.md            # This file
```

## Success Criteria

A successful test run should show:

1. ✅ All files uploaded successfully
2. ✅ Phone data processed (location, activity, steps, etc.)
3. ✅ Garmin data processed (heart rate, stress, steps)
4. ✅ Daily summaries generated
5. ✅ Data appears in dashboard
6. ✅ No errors in processing logs

If all criteria are met, the pipeline is working correctly! 🎉
