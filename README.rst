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

Optional : Get the extra fixtures
-------------

Sometimes, you may need to import extra fixtures for account users & socialaccount.
You just need to copy the corresponding json files into ./config/fixtures/.
And they will be copied in the docker image in the next step.

Build docker images
--------------

  # sudo docker-compose build

Setup with initial data
--------------

  # sudo docker-compose run --rm djangoapp ./config/setup.sh

Start
--------------

  # sudo docker-compose up


LICENSE: BSD
