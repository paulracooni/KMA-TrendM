FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV dev
ENV DOCKER_CONTAINER 1

RUN mkdir /app
WORKDIR /app



COPY .env .
COPY .project-root .

COPY tasks.py .
COPY data data
COPY utils utils
COPY models models
COPY modules modules

ADD requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

ADD migrations.json .
RUN ["pem", "watch"]
RUN ["pem", "migrate"]