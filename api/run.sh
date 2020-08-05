#!/bin/bash
set -x
export SIMPLE_SETTINGS=settings
exec bash -c "gunicorn --bind 0.0.0.0:5000 --workers 5 app:app --log-level debug --timeout 120"
$WORKER worker --web-port=$WORKER_PORT

