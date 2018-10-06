tucat
==============================

TuCat is a generic tool to extract data from APIs

Installation guide for Debian/Ubuntu
--------------
Prerequisites:
Docker & Docker Compose

Clone the repository
-------------
  git clone https://github.com/natoinet/tucat
  
  cd tucat

Copy the .env.example file into .env and edit the .env file
--------------
Run the following and copy the result in SECRET_KEY in the .env file
  python -c 'import random; result = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]); print(result)'


Build docker images
--------------
# sudo docker-compose build

Setup with initial data
--------------
# sudo ./config/setup.sh

Start
# sudo docker-compose up

LICENSE: BSD
