FROM python:3.11-slim-buster

WORKDIR /app

RUN apt update

RUN apt install curl -y

RUN pip3 install --upgrade pip

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH=/app

COPY . /app/nestipy

WORKDIR /app/nestipy

RUN pip3 install -e .

WORKDIR /app/nestipy/example

CMD ["nestipy", "start", "--dev"]