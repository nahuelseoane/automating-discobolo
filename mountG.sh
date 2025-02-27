# Checking if the file is accesible
ls -lh "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"

# unmount
sudo umount /mnt/g
# mount
sudo mount -t drvfs G: /mnt/g -o metadata
# verify
ls -l /mnt/g
