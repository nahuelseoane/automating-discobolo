#!/bin/bash

echo "🚀 Starting Discobolo Automation Pipeline..."

# ✅ Save environment variables for debugging
printenv > ./logs/cron_env.log

# Step 1: Check G Drive
echo "🔹 Step 1: Checking G Drive access"
bash discobolo/scripts/check_and_remount.sh || { echo "❌ Error running check_and_remount.sh"; exit 1; }

# Step 2: Backups
echo "🔹 Step 2: Running backups"
python3 discobolo/scripts/backup_files.py || { echo "❌ Error running backup_files.py"; exit 1; }

# Step 3: Bank file downloads
echo "🔹 Step 3: Downloading bank movements"
discobolo transfers --download1 --download2 || { echo "❌ Error in transfers download"; exit 1; }

# Step 4: Update transfer file
echo "🔹 Step 4: Updating transfer file"
discobolo transfers --update1 || { echo "❌ Error in transfers update1"; exit 1; }

# Step 5: Add 'Jefe de Grupo'
echo "🔹 Step 5: Updating 'Jefe de Grupo'"
discobolo transfers --update2 || { echo "❌ Error in transfers update2"; exit 1; }

# Step 6: Load into Sytech
echo "🔹 Step 6: Running Sytech automation"
discobolo sytech || { echo "❌ Error in Sytech automation"; exit 1; }

# Step 7: Send emails
echo "🔹 Step 7: Sending emails"
discobolo emails || { echo "❌ Error sending emails"; exit 1; }

# Step 8: Download Morosos report
echo "🔹 Step 8: Downloading Morosos report"
discobolo morosos --download || { echo "❌ Error downloading Morosos report"; exit 1; }

# Step 9: Update Morosos main file
echo "🔹 Step 9: Updating Morosos main file"
discobolo morosos --update || { echo "❌ Error updating Morosos report"; exit 1; }

echo "✅ Discobolo automation pipeline completed successfully!"
