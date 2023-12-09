#!/bin/sh

flask db upgrade
gunicorn -w 3 -t 60 -b 0.0.0.0:5000 app:app