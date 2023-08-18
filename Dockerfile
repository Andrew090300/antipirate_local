FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /backend
WORKDIR /backend
ADD Antipirate_ver_2/requirements.txt /backend/
RUN pip install -r requirements.txt
RUN apt-get update \
  && apt-get install -y build-essential \
  && apt-get install -y libpq-dev \
  && apt-get install -y gettext \
  && apt-get install -y procps


ADD Antipirate_ver_2 /backend/
