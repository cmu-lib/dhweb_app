# DH Conferences CRUD App

Application for editing, searching, and browsing historical DH conference abstracts.

Development lead: [Matthew Lincoln](https://matthewlincoln.net)

## Overview

This is a Django application orchestrated with Docker Compose, comprising 4 key services:

### nginx

The application is served behind nginx. `/nginx/nginx.template` shows the suggested formation of your `default.conf` file, setting up the reverse proxy to the Django service and serving the static files. the `/nginx` folder is passed as a volume to `/etc/nginx/conf.d` in the nginx docker container.

### memcached

Cache set up for Django

### postgres

The Django app relies on several [PostgreSQL-only functions and fields](https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/fields/), including its serviceable full-text search. Data is stored in a named `db` docker volume.

`make backup` will dump the database to the `/data` folder

### django

This is the core Django service, which builds from `/dh_abstracts/Dockerfile`. The python libraries are specified in `/dh_abstracts/requirements.txt`, installed when the Dockerfile is built.

## Deployment

Running this stack locally or in production requires an `.env` file based on `.env.template`, with selected db password and secret, and the proper hostname, email server etc.

In production we currently use gunicorn to serve, so the `SERVE_COMMAND` is set to `'gunicorn dhweb.wsgi -b 0.0.0.0:8000'`

## Updates

Update nginx, memcached, and postgres versions by incrementing their version tags in `docker-compose.yml`

Update underlying Python version in `dh_abstracts/Dockerfile`

Update python packages in `requirements.txt`.