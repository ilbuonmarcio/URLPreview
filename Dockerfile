FROM python:3.13.2-bookworm

RUN apt update && apt upgrade -y

RUN apt install firefox-esr wget -y
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.36.0-linux64.tar.gz && rm geckodriver-v0.36.0-linux64.tar.gz && ls -lah

RUN mkdir /app
RUN mkdir /app/tmp
RUN cp geckodriver /app/geckodriver
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY src/main.py /app/main.py

CMD ["python", "/app/main.py"]