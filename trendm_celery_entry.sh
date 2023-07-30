#!/bin/bash
pem watch
pem migrate
celery -A tasks worker --loglevel=INFO -B