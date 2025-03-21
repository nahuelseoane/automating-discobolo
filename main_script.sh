#!/bin/bash
touch /tmp/roadmap_ran.txt
cd /home/jotaene/PROYECTOS/AutoDiscoEmails/
source venv/bin/activate
echo "[$(date)] Script started" >> ./roadmap.log

./roadmap.sh >> ./roadmap.log 2>&1

echo "[$(date)] Script finished" >> ./roadmap.log