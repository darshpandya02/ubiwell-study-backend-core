#!/bin/bash

# Study Framework - Data Processing Script
# This script processes phone data, Garmin files, and generates summaries

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDY_DIR="$(dirname "$SCRIPT_DIR")"

# Set environment variables
export PYTHONPATH="${STUDY_DIR}:${PYTHONPATH}"
export STUDY_CONFIG_FILE="${STUDY_DIR}/config/study_config.json"

# Function to add timestamp to echo statements
log_echo() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --action ACTION     Action to perform:"
    echo "                      - process_data: Process phone data for all users"
    echo "                      - generate_summaries: Generate daily summaries"
    echo "                      - process_garmin: Process Garmin FIT files"
    echo "  --user USER         Specific user to process (optional)"
    echo "  --date DATE         Specific date in YYYY-MM-DD format (optional)"
    echo "  --env ENV           Conda environment name (default: study-env)"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --action process_data"
    echo "  $0 --action process_data --user user123"
    echo "  $0 --action generate_summaries --date 2024-01-15"
    echo "  $0 --action process_garmin"
}

# Default values
ACTION=""
USER=""
DATE=""
ENV_NAME="study-env"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --action)
            ACTION="$2"
            shift 2
            ;;
        --user)
            USER="$2"
            shift 2
            ;;
        --date)
            DATE="$2"
            shift 2
            ;;
        --env)
            ENV_NAME="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            log_echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if action is provided
if [[ -z "$ACTION" ]]; then
    log_echo "Error: --action is required"
    show_usage
    exit 1
fi

# Check if conda is available
if ! command -v conda &> /dev/null; then
    log_echo "Error: conda is not installed or not in PATH"
    exit 1
fi

# Activate conda environment
log_echo "Activating conda environment: $ENV_NAME"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

if [[ $? -ne 0 ]]; then
    log_echo "Error: Failed to activate conda environment: $ENV_NAME"
    exit 1
fi

# Change to study directory
cd "$STUDY_DIR"

log_echo "Starting data processing..."
log_echo "Action: $ACTION"
if [[ -n "$USER" ]]; then
    log_echo "User: $USER"
fi
if [[ -n "$DATE" ]]; then
    log_echo "Date: $DATE"
fi
log_echo "Study directory: $STUDY_DIR"
echo ""

# Execute the appropriate action
case "$ACTION" in
    process_data)
        if [[ -n "$USER" ]]; then
            log_echo "Processing data for user: $USER"
            python -m study_framework_core.core.processing_scripts --action process_data --user "$USER"
        else
            log_echo "Processing data for all users"
            python -m study_framework_core.core.processing_scripts --action process_data
        fi
        ;;
    generate_summaries)
        if [[ -n "$DATE" ]]; then
            log_echo "Generating summaries for date: $DATE"
            python -m study_framework_core.core.processing_scripts --action generate_summaries --date "$DATE"
        else
            log_echo "Generating summaries for yesterday"
            python -m study_framework_core.core.processing_scripts --action generate_summaries
        fi
        ;;
    process_garmin)
        log_echo "Processing Garmin FIT files"
        python -m study_framework_core.core.processing_scripts --action process_garmin
        ;;
    *)
        log_echo "Error: Unknown action: $ACTION"
        show_usage
        exit 1
        ;;
esac

# Check exit status
if [[ $? -eq 0 ]]; then
    echo ""
    log_echo "✅ Data processing completed successfully!"
else
    echo ""
    log_echo "❌ Data processing failed!"
    exit 1
fi
