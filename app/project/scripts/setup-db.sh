#! /usr/bin/sh

set -e

python project/manage.py makemigrations trackapp
echo "Migrations created."

python project/manage.py migrate
echo "Migrations completed."
