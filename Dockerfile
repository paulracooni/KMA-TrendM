FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV dev
ENV DOCKER_CONTAINER 1

RUN mkdir /app
WORKDIR /app

ADD .env .
ADD .project-root .
ADD migrations.json .
ADD trendm_celery_entry.sh .
RUN chmod 655 trendm_celery_entry.sh

ADD tasks.py .
ADD src src
ADD data data
ADD tests tests

ADD requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

