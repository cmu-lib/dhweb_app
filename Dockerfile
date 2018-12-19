FROM python:3.6
ADD . /vol/dh
WORKDIR /vol/dh
RUN apt-get update
RUN pip install -r requirements.txt
