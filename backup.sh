#!/bin/bash

docker-compose exec dh-web python manage.py dumpdata -e contenttypes --indent 2 -o /vol/data/backups/backup.json
cd /vol/data/backups
git add .
DATE=`date +%Y-%m-%d`
git commit -m "incremental backup $DATE"
