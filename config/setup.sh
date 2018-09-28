#!/bin/bash

sudo docker-compose run --rm djangoapp python manage.py migrate
sudo docker-compose run --rm djangoapp python manage.py createsuperuser
sudo docker-compose run --rm djangoapp chmod +x ./config/fixtures/load.sh
sudo docker-compose run --rm djangoapp ./config/fixtures/load.sh
