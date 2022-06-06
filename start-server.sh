#!/usr/bin/env bash
# start-server.sh
(cd /app && python3 manage.py migrate)
(cd /app; gunicorn carona_parque.wsgi --user www-data --bind 0.0.0.0:8000 --workers 3) &
nginx -g "daemon off;"
