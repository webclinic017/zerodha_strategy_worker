FROM python:3.8-slim-buster

RUN apt-get update -y

RUN apt-get install redis -y

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get install -y wget tar gcc build-essential

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
  && tar -xzf ta-lib-0.4.0-src.tar.gz \
  && rm ta-lib-0.4.0-src.tar.gz \
  && cd ta-lib/ \
  && ./configure --prefix=/usr \
  && make \
  && make install \
  && cd ~ \
  && rm -rf ta-lib/ \
  && pip install ta-lib

COPY . .

RUN redis-server --daemonize yes

CMD ["python", "app.py"]