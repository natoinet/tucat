#!/bin/bash

function importfixtures {
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

importfixtures admin_interface_theme_tucat auth account users socialaccount
