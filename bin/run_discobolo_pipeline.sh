#!/bin/bash
PROJECT_DIR="/home/jotaene/projects/automating-discobolo"

# Move to project root directory
cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

# Fix import errors
export PYTHONPATH=$PROJECT_DIR

LOG="$PROJECT_DIR/logs/automation_pipeline.log"

# DEBUG: Log environment at cron time
env > ./logs/env_from_cron.log

echo "Reached discobolo execution point" >> ./logs/automation_pipeline.log
# Create temp lock/trace file
touch /tmp/roadmap_ran.txt

echo "[$(date)] Python used:" >> ./logs/automation_pipeline.log
which python >> ./logs/automation_pipeline.log

# Log start timestamp
echo "[$(date)] Script started" >> ./logs/automation_pipeline.log

# Run automation pipeline
bash ./bin/automation_pipeline.sh >> ./logs/automation_pipeline.log 2>&1

# Log end timestamp
echo "[$(date)] Script finished" >> ./logs/automation_pipeline.log