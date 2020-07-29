#!/bin/bash
set -x
export SIMPLE_SETTINGS=settings
exec bash -c "python run.py"
$WORKER worker --web-port=$WORKER_PORT
