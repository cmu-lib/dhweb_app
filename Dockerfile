FROM python:3.7.3
ADD . /vol/dh
WORKDIR /vol/dh
RUN apt-get update
RUN pip install -r requirements.txt
WORKDIR /vol/dh/app
EXPOSE 8000
