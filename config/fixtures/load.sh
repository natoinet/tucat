#!/bin/bash

python manage.py loaddata admin_interface_theme_tucat.json

python manage.py loaddata account.json
python manage.py loaddata users.json
python manage.py loaddata auth.json

python manage.py loaddata application.json

python manage.py loaddata twitter_extraction.exportationformat.json
python manage.py loaddata twitter_extraction.exportationtype.json
python manage.py loaddata twitter_extraction.twitterlistextraction.json

python manage.py loaddata socialaccount.json
