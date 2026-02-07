#!/bin/bash
# Setup script for configuring the daily job refresh cron job
# This script helps set up a cron job to run at 3am EST daily

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="$(which python3)"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

# Use virtual environment python if it exists
if [ -f "$VENV_PYTHON" ]; then
    PYTHON_PATH="$VENV_PYTHON"
fi

echo "Tech Job Board - Cron Job Setup"
echo "================================"
echo ""
echo "This will set up a daily cron job to refresh jobs at 3pm EST."
echo ""
echo "Python path: $PYTHON_PATH"
echo "Script path: $SCRIPT_DIR/app/cron_job.py"
echo ""

# Create the cron job command
# 0 20 * * * means: minute=0, hour=20 (UTC), every day
# 8pm UTC = 3pm EST (UTC-5)
CRON_CMD="0 20 * * * cd $SCRIPT_DIR && $PYTHON_PATH app/cron_job.py >> $SCRIPT_DIR/cron_job.log 2>&1"

echo "Cron job command:"
echo "$CRON_CMD"
echo ""
echo "To install this cron job, run:"
echo ""
echo "(crontab -l 2>/dev/null; echo \"$CRON_CMD\") | crontab -"
echo ""
echo "To view your current crontab:"
echo "crontab -l"
echo ""
echo "To remove the cron job later:"
echo "crontab -e  # then delete the line containing 'cron_job.py'"
echo ""
echo "Note: Logs will be written to $SCRIPT_DIR/cron_job.log"
