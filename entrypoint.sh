#!/usr/bin/env bash
set -e

exec uwsgi --http 0.0.0.0:5000 \
    --wsgi-file authelia-manager.py \
    --callable app \
    --workers 4 \
    --master \
    --enable-threads \
    --log-master \
    --disable-logging \
    --log-4xx \
    --log-5xx
