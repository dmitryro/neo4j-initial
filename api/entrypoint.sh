#!/bin/sh
### Check if a directory does not exist ###
#
#exec python manage.py db current
#exec python manage.py db migrate
#exec python manage.py db upgrade
#exec python manage.py db current
#exec python manage.py db migrate
#exec gunicorn --bind 0.0.0.0:5000 --workers 5 app:app --log-level debug --timeout 240
#exec alembic upgrade head
exec alembic current
exec alembic upgrade
exec alembic revision --autogenerate -m "create tables"
