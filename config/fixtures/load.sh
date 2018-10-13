#!/bin/bash

python manage.py loaddata admin_interface_theme_tucat.json

python manage.py loaddata auth.json

if [ -e account.json ]
then
  python manage.py loaddata account.json
fi

if [ -e users.json ]
then
  python manage.py loaddata users.json
fi

if [ -e socialaccount.json ]
then
  python manage.py loaddata socialaccount.json
fi
