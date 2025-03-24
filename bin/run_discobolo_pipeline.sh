#!/bin/bash

# Create temp lock/trace file
touch /tmp/roadmap_ran.txt

# Move to project root directory
cd /home/jotaene/proyectos/automating-discobolo/

# Activate virtual environment
source venv/bin/activate

# Log start timestamp
echo "[$(date)] Script started" >> ./logs/automation_pipeline.log

# Run automation pipeline
bash ./bin/automation_pipeline.sh >> ./logs/automation_pipeline.log 2>&1

# Log end timestamp
echo "[$(date)] Script finished" >> ./logs/automation_pipeline.log