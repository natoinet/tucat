#!/bin/bash

python manage.py loaddata admin_interface_theme_tucat.json

python manage.py loaddata auth.json

fixture=account
if [ -e config/fixtures/$fixture.json ]
then
  echo "Importing $fixture"
  python manage.py loaddata $fixture.json
else
  echo "No $fixture to import"
fi

fixture=users
if [ -e config/fixtures/$fixture.json ]
then
  echo "Importing $fixture"
  python manage.py loaddata $fixture.json
else
  echo "No $fixture to import"
fi

fixture=socialaccount
if [ -e config/fixtures/$fixture.json ]
then
  echo "Importing $fixture"
  python manage.py loaddata $fixture.json
else
  echo "No $fixture to import"
fi
