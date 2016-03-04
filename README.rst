tucat
==============================

TuCat is a generic tool to extract data from web APIs

Installation guide for Debian/Ubuntu
--------------
Prerequisites:
Python 3.4 or + with Virtualenv & virtualenvwrapper
Mongodb 2.6 or +
NGinx

Clone the repository
     # cd ~/src
     # git clone https://github.com/natoinet/tucat

Nginx setup
    # sudo cp ~/src/tucat/config/nginx/garbellador.com > /etc/nginx/sites-available
    # ln -s /etc/nginx/sites-available/garbellador.com /etc/nginx/sites-enabled/
    # service nginx restart

Gunicorn webserver installation
     # sudo apt-get install gunicorn

Install rabbit-mq server:
     # sudo vim /etc/apt/sources.list
          => add: deb http://www.rabbitmq.com/debian/ testing main
     # sudo apt-get install rabbitmq-server
Source: https://www.rabbitmq.com/install-debian.html

The broker can then be started or stopped with the following command:
     # sudo service rabbitmq-server start

Install postgresql:
     # sudo apt-get install postgresql
     # sudo apt-get install postgresql-contrib
     # sudo apt-get install libpq-dev

Create dj_tucat database & users
     # sudo -u postgres -i
     # psql
          create user garbellador with password ‘yourpasswordhere';
          create database dj_tucat;
          grant all privileges on database dj_tucat to garbellador;
          \q
     # exit

Install supervisord:
     # sudo pip install supervisor

Supervisord Config:
     # sudo cp ~/src/tucat/config/supervisord/supervisord.conf > /etc/supervisord.conf

Gunicorn Supervisord config
     # sudo cp ~/src/tucat/config/supervisord/tucat.conf > /etc/tucat.conf

Celery Supervisord config
     # sudo cp ~/src/tucat/config/supervisord/celerybeat.conf > /etc/celerybeat.conf
     # sudo cp ~/src/tucat/config/supervisord/celeryd.conf > /etc/celeryd.conf

Start supervisord at startup
    # sudo curl https://gist.github.com/howthebodyworks/176149/raw/88d0d68c4af22a7474ad1d011659ea2d27e35b8d/supervisord.sh > /etc/init.d/supervisord
    # sudo mkdir /var/log/supervisord/
    # sudo chmod +x /etc/init.d/supervisord
    # sudo update-rc.d supervisord defaults

Create & install the virtualenv
     # mkvirtualenv --python=/usr/local/opt/python-3.4.1/bin/python3 -r requirements/test.txt tucat

Create a log folder
     # cd tucat
     # mkdir log

Create the local environment file
     # vim ~/src/tucat/.env
         DEBUG=on
         DJANGO_SETTINGS_MODULE=config.settings.production
         DATABASE_URL=postgres://garbellador:yourpasswordhere@localhost:5432/dj_tucat

Restart supervisord
     # sudo service supervisord restart
     # sudo supervisorctl
     # status


LICENSE: BSD

