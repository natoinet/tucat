tucat
==============================

TuCat is a generic tool to extract data from APIs

Installation guide for Debian/Ubuntu
--------------
Prerequisites:
Docker & Docker Compose

Edit the .env file
# python -c 'import random; result = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]); print(result)'
and copy the result into 

Clone the repository
# git clone https://github.com/natoinet/tucat
# cd tucat

Build docker images
# sudo docker-compose build

Setup with initial data
# sudo ./config/setup.sh

Start
# sudo docker-compose up

LICENSE: BSD
