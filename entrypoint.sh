#!/bin/bash

set -e

case $1 in

    prod)
        python manage.py wait_for_db
        python manage.py migrate
        python manage.py runserver 0.0.0.0:80
        echo "→ Running as prod mode"
        ;;

    dev)
        echo "→ Running as dev mode"
        python manage.py wait_for_db
        python manage.py migrate
        python manage.py runserver 0.0.0.0:80
        ;;

    *)
        exec "$@"
        ;;
esac
