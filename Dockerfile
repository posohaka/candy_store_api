FROM python:3.7 as base

RUN apt-get update && apt-get install -y \
  libpq5 \
  wait-for-it \
  && apt-get clean && rm -rf /var/lib/apt/lists/*


WORKDIR /app/src
COPY requirements.txt /app/src/
RUN pip install -r /app/src/requirements.txt

COPY ./ /app/src