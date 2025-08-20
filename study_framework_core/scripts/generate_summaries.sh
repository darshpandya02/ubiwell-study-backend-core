#!/bin/bash

# Study Framework - Daily Summary Generation Script
# This script generates daily summaries and plots for all users

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDY_DIR="$(dirname "$SCRIPT_DIR")"

# Set environment variables
export PYTHONPATH="${STUDY_DIR}:${PYTHONPATH}"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --date DATE         Specific date in YYYY-MM-DD format (default: last 2 hours)"
    echo "  --user USER         Specific user to process (optional)"
    echo "  --env ENV           Conda environment name (default: study-env)"
    echo "  --hours-back HOURS  Hours to look back for summaries (default: 2)"
    echo "  --plots             Also generate plots for the summaries"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Generate summaries for last 2 hours"
    echo "  $0 --date 2024-01-15  # Generate summaries for specific date"
    echo "  $0 --user user123     # Generate summaries for specific user"
    echo "  $0 --hours-back 4     # Generate summaries for last 4 hours"
    echo "  $0 --plots           # Generate summaries and plots"
}

# Default values
DATE=""
USER=""
ENV_NAME="study-env"
HOURS_BACK="2"
GENERATE_PLOTS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --date)
            DATE="$2"
            shift 2
            ;;
        --user)
            USER="$2"
            shift 2
            ;;
        --env)
            ENV_NAME="$2"
            shift 2
            ;;
        --hours-back)
            HOURS_BACK="$2"
            shift 2
            ;;
        --plots)
            GENERATE_PLOTS=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    exit 1
fi

# Activate conda environment
echo "Activating conda environment: $ENV_NAME"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

if [[ $? -ne 0 ]]; then
    echo "Error: Failed to activate conda environment: $ENV_NAME"
    exit 1
fi

# Change to study directory
cd "$STUDY_DIR"

echo "Starting summary generation..."
if [[ -n "$DATE" ]]; then
    echo "Date: $DATE"
else
    echo "Time range: Last $HOURS_BACK hours (default)"
fi
if [[ -n "$USER" ]]; then
    echo "User: $USER"
else
    echo "User: All users"
fi
echo "Generate plots: $GENERATE_PLOTS"
echo "Study directory: $STUDY_DIR"
echo ""

# Generate summaries
echo "🔄 Generating summaries..."
if [[ -n "$USER" ]]; then
    if [[ -n "$DATE" ]]; then
        python -m study_framework_core.core.processing_scripts --action generate_summaries --user "$USER" --date "$DATE"
    else
        python -m study_framework_core.core.processing_scripts --action generate_summaries --user "$USER" --hours-back "$HOURS_BACK"
    fi
else
    if [[ -n "$DATE" ]]; then
        python -m study_framework_core.core.processing_scripts --action generate_summaries --date "$DATE"
    else
        python -m study_framework_core.core.processing_scripts --action generate_summaries --hours-back "$HOURS_BACK"
    fi
fi

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to generate summaries!"
    exit 1
fi

echo "✅ Summaries generated successfully!"

# Generate plots if requested
if [[ "$GENERATE_PLOTS" == true ]]; then
    echo ""
    echo "🔄 Generating plots..."
    
    # Get the target date
    if [[ -n "$DATE" ]]; then
        TARGET_DATE="$DATE"
    else
        TARGET_DATE=$(date +%Y-%m-%d)
    fi
    
    # Generate plots for users
    if [[ -n "$USER" ]]; then
        python -c "
from study_framework_core.core.processing_scripts import DataProcessor
processor = DataProcessor()
processor.generate_plots('$USER', '$TARGET_DATE')
"
    else
        # Get all users and generate plots for each
        python -c "
from study_framework_core.core.processing_scripts import DataProcessor
from study_framework_core.core.handlers import get_db

processor = DataProcessor()
db = get_db()
users = db['users'].find({}, {'uid': 1})

for user_doc in users:
    uid = user_doc['uid']
    processor.generate_plots(uid, '$TARGET_DATE')
"
    fi
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Plots generated successfully!"
    else
        echo "❌ Failed to generate plots!"
        exit 1
    fi
fi

echo ""
echo "🎉 Summary generation completed successfully!"
