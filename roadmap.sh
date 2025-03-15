# 1️⃣ Save commands in my_script.sh
# 2️⃣ Make it executable (chmod +x my_script.sh)
# 3️⃣ Run it with ./my_script.sh
# 4️⃣ (Optional) Move it to /usr/local/bin/ for quick access

echo "🚀 Starting Discobolo Roadmap..."

# Step 1: Checking G accessibility
echo "🔹🔹🔹🔹🔹🔹🔹 Running checkup🔹🔹🔹🔹🔹🔹🔹 "
./check_and_remount.sh
if [ $? -ne 0 ]; then
    echo "❌ Error with 'check_and_remount.sh' "
    exit 1
fi
# Step 2: Backups
echo "🔹🔹🔹🔹🔹🔹🔹 Running backups🔹🔹🔹🔹🔹🔹🔹 "
python3 backup_files.py
if [ $? -ne 0 ]; then
    echo "❌ Error running backup_files.py"
    exit 1
fi

# Step 3: Update_bank_file.py
echo "🔹🔹🔹🔹🔹🔹🔹 Running transfer_file_update.py🔹🔹🔹🔹🔹🔹🔹 "
python3 transfer_file_update.py
if [ $? -ne 0 ]; then
    echo "❌ Error running transfer_file_update.py"
    exit 1
fi

# Step 4: jefe_de_grupo_update.py
echo "🔹🔹🔹🔹🔹🔹🔹 Running jefe_de_grupo_update.py🔹🔹🔹🔹🔹🔹🔹 "
python3 jefe_de_grupo_update.py
if [ $? -ne 0 ]; then
    echo "❌ Error running jefe_de_grupo_update.py"
    exit 1
fi

# Step 5: sytech_automate.py
echo "🔹🔹🔹🔹🔹🔹🔹 Running sytech_automate.py🔹🔹🔹🔹🔹🔹🔹 "
python3 sytech_automate.py
if [ $? -ne 0 ]; then
    echo "❌ Error running sytech_automate.py"
    exit 1
fi

# Step 6: Sending emails
echo "🔹🔹🔹🔹🔹🔹🔹 Sending emails...🔹🔹🔹🔹🔹🔹🔹"
python3 email_sending_automate.py

if [ $? -ne 0 ]; then
    echo "❌ Error running email_sending_automate.py"
    exit 1
fi

# Step 7: Morosos Report
echo "Do you want to create morosos report? (y/n)"
read -r user_input

if [ "$user_input" = "y" ] || [ "$user_input" = "Y" ]; then
    echo "🔹🔹🔹🔹🔹🔹🔹 Creating Morosos file🔹🔹🔹🔹🔹🔹🔹"
    python3 morosos_download.py

    if [ $? -ne 0 ]; then
        echo "❌ Error running morosos_daily_download.py"
        exit 1
    fi
    echo "  ✅ Morosos report successfully downloaded."

    echo "🔹🔹🔹🔹🔹🔹🔹 Updating Morosos Main file🔹🔹🔹🔹🔹🔹🔹"
    python3 morosos_update.py

    if [ $? -ne 0 ]; then
        echo "❌ Error running morosos_update.py"
        exit 1
    fi
else
    echo " ❌ Morosos file creation skipped."
fi
echo "✅ Roadmap execution completed!"
