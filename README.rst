tucat
==============================

TuCat is a generic tool to extract data from APIs

Installation guide for Debian/Ubuntu
--------------
Prerequisites:
Docker & Docker Compose

Clone the Tucat repository
-------------

  # git clone https://github.com/natoinet/tucat

  # cd tucat

Copy the .env.example file into .env and edit the .env file
--------------

Run the following and copy the result in SECRET_KEY in the .env file

  # python -c 'import random; result = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]); print(result)'

Clone the twitter_extraction repository
-------------

  # cd tucat

  # git clone https://github.com/natoinet/twitter_extraction

  # git clone https://github.com/natoinet/twitter_streaming

  # cd ..

Build docker images
--------------

  # sudo docker-compose build

Setup with initial data
--------------

  # sudo docker-compose run --rm djangoapp ./config/setup.sh

Create a docker alias for the TucatApp container
--------------

  # alias doc_tucat='sudo docker ps -f name=tucat_django -q'

Start
--------------

  # sudo docker-compose up

LICENSE: BSD
