FROM python:3.13

RUN apt update && apt upgrade -y
RUN mkdir /app
WORKDIR /app
COPY src/main.py /app/main.py
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt