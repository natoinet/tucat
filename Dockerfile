## Tucat source code https://github.com/natoinet/tucat
## docker-compose build

FROM python:3.6
LABEL authors="Antoine Brunel <antoine.brunel@gmail.com> & Victor Esteban <victor@limogin.com>"
LABEL release=1.0

ARG apphome
ARG applog

RUN echo ${apphome} ${applog}
ENV PYTHONUNBUFFERED 1
ENV APPHOME ${apphome}
ENV APPLOG ${applog}

#### Install Mongodb Entreprise tools
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
RUN echo 'deb http://repo.mongodb.com/apt/debian stretch/mongodb-enterprise/4.0 main' | tee /etc/apt/sources.list.d/mongodb-enterprise.list
RUN apt-get update
RUN apt-get install -y mongodb-enterprise-shell mongodb-enterprise-tools

RUN mkdir -p ${APPHOME}
RUN mkdir -p ${APPLOG}
RUN chmod 700 -R ${APPLOG}

WORKDIR ${APPHOME}

# Install dependencies
ADD ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

## Install Tucat
RUN echo "Install Tucat Application & plugings" && \
	git clone https://github.com/natoinet/tucat ${APPHOME} && \
	cd ${APPHOME}/tucat

# Environment configuration file
COPY ./.env ${APPHOME}

# Copy additional fixtures
COPY ./config/fixtures/*.json ${APPHOME}/config/fixtures/

RUN echo "Supervisor Configuration " && \
    mkdir -p /var/log/supervisor && \
    mkdir -p /etc/supervisor && \
    mkdir -p /etc/supervisor/conf.d

RUN echo "Creating Django user" && \
		useradd -M --system -u 1000 tucat

ADD config/supervisord/supervisord.conf /etc/supervisor/supervisord.conf
ADD config/supervisord/conf.d/celerybeat.conf  /etc/supervisor/conf.d/celerybeat.conf
ADD config/supervisord/conf.d/celeryd.conf     /etc/supervisor/conf.d/celeryd.conf
#ADD config/supervisord/conf.d/flower.conf     /etc/supervisor/conf.d/flower.conf
ADD config/supervisord/conf.d/tucat.conf       /etc/supervisor/conf.d/tucat.conf

# Collect static files
RUN chown -R tucat ${APPHOME}/..
RUN su tucat && cd ${APPHOME} && python manage.py collectstatic --no-input

# Setting-up logs
RUN chown -R tucat ${APPLOG} && \
    chgrp tucat -R ${APPLOG} && \
    chmod g+w -R ${APPLOG} && \
    chmod g+s -R ${APPLOG}

# Expose the port
EXPOSE 8000

# Entry point for initial Django initial migrations
COPY ./entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint
RUN chown tucat /entrypoint

ENTRYPOINT ["/entrypoint"]
