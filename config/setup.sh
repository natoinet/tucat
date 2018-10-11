#!/bin/bash

sleep 5
python manage.py makemigrations admin_interface auth sessions sites django_celery_beat core users
python manage.py migrate --fake-initial

python manage.py createsuperuser
chmod +x ./config/fixtures/load.sh
./config/fixtures/load.sh
