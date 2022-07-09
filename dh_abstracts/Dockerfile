FROM python:3.9.13
WORKDIR /vol/dh
ADD requirements.txt /vol/dh
RUN pip install -r requirements.txt
ADD . /vol/dh
WORKDIR /vol/dh/app
EXPOSE 8000
