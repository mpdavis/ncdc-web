#!/bin/bash
filename = `date +%m-%d-%Y-%H-%M-%S.dmp`
mongodump --port 27017 --username="db_user" --password="super_secret_db_password" --out "$filename"
tar -zcf "$filename.tar.gz" "$filename"
openssl aes-256-cbc -salt -in "$filename.tar.gz" -out "$filename.tar.gz.aes" -k "encryption_password"
rsync -az -e "ssh -i rsync-private-key" "$filename.tar.gz.aes" backupuser@10.0.0.50:/home/backupuser/backups/web
rm -rf "$filename"
rm -f "$filename.tar.gz"
rm -f "$filename.tar.gz.aes"
echo "Finished backups"