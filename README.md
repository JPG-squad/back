# AWS Hackathon 2023

## backend
JPG -- backend

### Commands used:
```bash
poetry install
poetry add black --group dev
docker-compose run --rm back bash -c "django-admin startproject app ."
docker-compose build
docker-compose up
```

Then, the backend runs in http://localhost:8777
And we can find the api documentation on: http://localhost:8777/api/docs

Command for creating `user` django app:
```bash
docker-compose run --rm back bash -c "python manage.py startapp user"
```
For the `user` app, after creating, we have deleted: migrations, admin and models because these are going to be in the `core` app.

Format all the project in the beggining:
```bash
black .
```

Test command (out-of-the-box Django Test Framework):
```bash
docker-compose run --rm back bash -c "python manage.py test"
docker-compose exec back bash -c "python manage.py test"
```

Lint command:
```bash
docker-compose run --rm back bash -c "flake8"
or
docker-compose exec back bash -c "flake8"
```

Create super user:
```bash
docker-compose run --rm back bash -c "python manage.py createsuperuser"
or
docker-compose exec back bash -c "python manage.py createsuperuser"
````
