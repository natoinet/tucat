## Tucat source code https://github.com/natoinet/tucat
## docker-compose build

FROM python:latest
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
#RUN touch ${APPLOG}/celery_beat.log ${APPLOG}/celery_worker.log ${APPLOG}/gunicorn.log
RUN chmod 700 -R ${APPLOG}

WORKDIR ${APPHOME}

#RUN addgroup --system django \
#    && adduser --system django --ingroup django

# Install dependencies
ADD ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

## Install Tucat
RUN echo "Install Tucat Application & plugings" && \
	git clone https://github.com/natoinet/tucat ${APPHOME} && \
	cd ${APPHOME}/tucat && \
	git clone https://github.com/natoinet/twitter_extraction && \
	git clone https://github.com/natoinet/twitter_streaming

COPY ./.env ${APPHOME}

RUN echo "Supervidor Configuration " && \
    mkdir -p /var/log/supervisor && \
    mkdir -p /etc/supervisor && \
    mkdir -p /etc/supervisor/conf.d

RUN echo "Creating Django user" && \
		useradd -M --system -u 1000 tucat

ADD config/supervisord/supervisord.conf /etc/supervisor/supervisord.conf
ADD config/supervisord/conf.d/celerybeat.conf  /etc/supervisor/conf.d/celerybeat.conf
ADD config/supervisord/conf.d/celeryd.conf     /etc/supervisor/conf.d/celeryd.conf
ADD config/supervisord/conf.d/tucat.conf       /etc/supervisor/conf.d/tucat.conf

RUN > ${APPLOG}/logging.log > ${APPLOG}/gunicorn.log > ${APPLOG}/celery_worker.log > ${APPLOG}/celery_beat.log
RUN chown -R tucat ${APPHOME}/..
RUN chown -R tucat ${APPLOG}/ && \
    chgrp tucat ${APPLOG} && \
    chmod g+w ${APPLOG} && \
    chmod g+s ${APPLOG} 
    #umask 002

COPY ./entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint
RUN chown tucat /entrypoint

# Expose the port
EXPOSE 8000

RUN su tucat && cd ${APPHOME} && python manage.py collectstatic --no-input

ENTRYPOINT ["/entrypoint"]
