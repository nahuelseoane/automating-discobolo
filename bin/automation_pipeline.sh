#!/bin/bash

echo "🚀 Starting Discobolo Automation Pipeline..."


# Export current environment info
printenv > ./logs/cron_env.log

# Step 1: Check G Drive
echo "🔹 Step 1: Checking G Drive access"
bash ./scripts/check_and_remount.sh
if [ $? -ne 0 ]; then
    echo "❌ Error running check_and_remount.sh"
    exit 1
fi

# Step 2: Backups
echo "🔹 Step 2: Running backups"
python3 ./scripts/backup_files.py
if [ $? -ne 0 ]; then
    echo "❌ Error running backup_files.py"
    exit 1
fi

# Step 3: Download Bank Movements
echo "🔹 Step 3: Downloading Bank Movements"
python3 ./scripts/bank_movements_download.py
if [ $? -ne 0 ]; then
    echo "❌ Error running bank_movements_download.py"
    exit 1
fi

# Step 4: Transfer File Update
echo "🔹 Step 4: Updating Transfer File"
python3 ./scripts/transfer_file_update.py
if [ $? -ne 0 ]; then
    echo "❌ Error running transfer_file_update.py"
    exit 1
fi

# Step 5: Jefe de Grupo Update
echo "🔹 Step 5: Updating Jefe de Grupo"
python3 ./scripts/jefe_de_grupo_update.py
if [ $? -ne 0 ]; then
    echo "❌ Error running jefe_de_grupo_update.py"
    exit 1
fi

# Step 6: Sytech Automation
echo "🔹 Step 6: Running Sytech Automation"
python3 ./scripts/sytech_automate.py
if [ $? -ne 0 ]; then
    echo "❌ Error running sytech_automate.py"
    exit 1
fi

# Step 7: Sending Emails
echo "🔹 Step 7: Sending Emails"
python3 ./scripts/email_sending_automate.py
if [ $? -ne 0 ]; then
    echo "❌ Error running email_sending_automate.py"
    exit 1
fi

# Step 8: Morosos Report
echo "🔹 Step 8: Creating Morosos Report"
python3 ./scripts/morosos_download.py
if [ $? -ne 0 ]; then
    echo "❌ Error running morosos_download.py"
    exit 1
fi

echo "🔹 Step 9: Updating Morosos Main File"
python3 ./scripts/morosos_update.py
if [ $? -ne 0 ]; then
    echo "❌ Error running morosos_update.py"
    exit 1
fi

echo "✅ Discobolo automation pipeline completed successfully!"
