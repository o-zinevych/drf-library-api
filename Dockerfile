FROM python:3.12.1-alpine3.18
LABEL maintainer="olgazinevych@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
