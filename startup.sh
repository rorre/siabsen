#!/bin/sh
echo "Waiting for postgres and migration..."
while true
do
    flask db upgrade
    if [ $? = 0 ]; then
        break
    fi

    echo -n "."
done

gunicorn -w 3 -t 60 -b 0.0.0.0:5000 app:app