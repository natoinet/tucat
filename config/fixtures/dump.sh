#!/bin/bash

python manage.py dumpdata application --indent 4 -o ~/application.json
python manage.py dumpdata auth --indent 4 -o ~/auth.json
python manage.py dumpdata sites --indent 4 -o ~/sites.json
python manage.py dumpdata account --indent 4 -o ~/account.json
python manage.py dumpdata socialaccount --indent 4 -o ~/socialaccount.json
python manage.py dumpdata users --indent 4 -o ~/users.json
python manage.py dumpdata twitter_extraction.exportationtype --indent 4 -o ~/twitter_extraction.exportationtype.json
python manage.py dumpdata twitter_extraction.exportationformat --indent 4 -o ~/twitter_extraction.exportationformat.json
python manage.py dumpdata twitter_extraction.twitterlistextraction --indent 4 -o ~/twitter_extraction.twitterlistextraction.json
