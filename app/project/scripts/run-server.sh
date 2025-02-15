#! /usr/bin/sh

set -e
python project/manage.py runserver "0.0.0.0:${APP_PORT}"
