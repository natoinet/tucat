#!/bin/bash

sudo docker-compose down
sudo docker system prune -a -f
sudo docker volume prune -f
