<h1 align="center"> Backend  </h1> <br>

<p align="center">
  AWS Hackathon for Good, Squad JPG backend project
</p>


## Table of Contents
- [Table of Contents](#table-of-contents)
- [Setup](#setup)
  - [Requirements](#requirements)
  - [One time configuration](#one-time-configuration)
  - [Build](#build)
  - [Start](#start)
- [Local development](#local-development)
  - [Managing databases](#managing-databases)
  - [Debugging](#debugging)
  - [Tests](#tests)
- [Deployment](#deployment)
  - [On push main publish a new version](#on-push-main-publish-a-new-version)


## Setup

### Requirements

Check that you have installed:
* Poetry
* Pre-commit

### One time configuration


In a terminal inside this project directory:
Configure poetry (if it not already exists, Poetry will create a new virtual enviornment in this directory too, in a `.venv` folder):
```bash
poetry install
```
And once installed all the libraries with poetry, remember to configiure pre-commit and autoupdate to set the versions of the libraries to the required by pre-commit:
```bash
pre-commit install
pre-commit autoupdate
```
Create network:
```bash
docker network create --driver bridge --subnet 172.18.0.0/16 jpg-network > /dev/null 2>&1
```

### Build

```bash
docker-compose build --ssh default
```

### Start
In order to start the Base service we need to start the servicies that it uses, to do it execute:
```bash
docker-compose up
```
You can now execute service endpoints using Swagger UI: open http://localhost:8777/api/docs

Django admin is also available: open http://localhost:8777/admin


## Local development

### Managing databases
For developing propouses we have databases dumps under the [dumps](dumps) folder, you can restore them with the following command:
```bash
bash scripts/restore.sh
```

Also you can create dumps of your current databases and save them under the [dumps](dumps) folder with the following command:
```bash
bash scripts/dump.sh
```

Will create a day-month-year-hour-minute.dump file and then anyone can restore it and have updated data.

### Debugging
TODO
To raise the service in debug mode, first you must update the DEBUGPY environment variable at [env-local](env-local):
```bash
DEBUGPY=True
```
Then you can start the service as explained at [Start](###start).

Once the service has started, open the debug view on vscode:

<b>command + alt + D</b>

Then we can attach to data-service configuration to debug the service in general, you can put a breakpoint inside any file of the `src` directory and the application will stop once it reaches the point.

### Tests
STILL TO DO

## Deployment

In this repository we have two principal brances: **main**.
And the following CI / CD pipelines:

### On push main publish a new version

1. Automatic bumps a new version tag from main branch and creates a release with it.
2. Builds and pushes the new docker image from the main branch to the ECR and deploys with blue/green deployment.
