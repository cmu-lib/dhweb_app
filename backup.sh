#!/bin/bash

set -e

source /vol/dh_web/.env

/home/mlincoln/.local/bin/docker-compose -f /vol/dh_web/docker-compose.yml --project-directory /vol/dh_web/ exec -T dh-web python manage.py dumpdata -e contenttypes -e sessions --indent 2 -o /vol/data/backups/backup.json
cd /vol/data/backups
/usr/bin/git add .
DATE=`date +%Y-%m-%d`
/usr/bin/git commit -m "incremental backup $DATE"
