FROM python:3.8-slim-buster

RUN apt-get update -y

RUN apt-get install redis -y

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN redis-server --daemonize yes

CMD ["python", "app.py"]