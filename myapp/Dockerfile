FROM python:3.11-slim-buster

WORKDIR /app

RUN apt update

RUN pip3 install --upgrade pip

RUN pip3 install nestipy-cli nestipy

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

CMD ["nestipy", "start", "--dev"]