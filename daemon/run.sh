#!/bin/bash
set -x
export SIMPLE_SETTINGS=settings
exec bash -c "faust -A service worker -l info"
$WORKER worker --web-port=$WORKER_PORT
