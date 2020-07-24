#!/bin/bash
set -x
export SIMPLE_SETTINGS=settings
python load_initial.py
exec bash -c "faust -A service worker -l info"
$WORKER worker --web-port=$WORKER_PORT
