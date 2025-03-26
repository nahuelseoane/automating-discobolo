#!/bin/bash
echo "Reached discobolo execution point" >> ./logs/automation_pipeline.log
# Create temp lock/trace file
touch /tmp/roadmap_ran.txt

# Set environment
./bin/set_env.sh

echo "[$(date)] Python used:" >> ./logs/automation_pipeline.log
which python >> ./logs/automation_pipeline.log

# Log start timestamp
echo "[$(date)] Script started" >> ./logs/automation_pipeline.log

# Run automation pipeline
discobolo run >> ./logs/automation_pipeline.log 2>&1

# Log end timestamp
echo "[$(date)] Script finished" >> ./logs/automation_pipeline.log