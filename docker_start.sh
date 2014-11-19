#!/bin/sh

: ${API_ENV:='devel'}

if [ "$API_ENV" = 'devel' ]; then
    git describe > /etc/d8o/api/VERSION
fi

python run.py
