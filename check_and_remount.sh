# Checking if the file is accesible
FILE_PATH="${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"

echo " Checkgin if the file is accesible..."
if ls -lh "$FILE_PATH" >/dev/null 2>&1; then
    echo "✅ File is accessible."
else
    echo "❌ File not found... remounting drive:"

    echo "🔻 Unmounting G..."
    sudo umount /mnt/g

    echo "🔺 Mounting G..."
    sudo mount -t drvfs G: /mnt/g -o metadata

    echo "Verifying after remount"

    if ls -l /mnt/g >/dev/null 2>&1; then
        echo "✅ File is now accesible"
    else
        echo "❌ File still not found, try manually."
    fi
fi
