#!/bin/bash

python manage.py loaddata admin_interface_theme_tucat.json

python manage.py loaddata auth.json

import account users socialaccount

function import {
  for fixture in "$@"
  do
    if [ -e config/fixtures/$fixture.json ]
    then
      echo "Importing $fixture"
      python manage.py loaddata $fixture.json
    else
      echo "No $fixture to import"
    fi
  done
}
