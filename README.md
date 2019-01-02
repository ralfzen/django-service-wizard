[![Build Status](http://drone.humanitec.io/api/badges/Humanitec/django-service-wizard/status.svg)](http://drone.humanitec.io/Humanitec/django-service-wizard)

# django-service-wizard

A Django (Micro)Service wizard for the Humanitec Platform Walhall. This will
help you to setup your a project from scratch.

The Django version installed is specified in `requirements/base.txt`. The
project will be created for Python version 3
(see `service_builder/templates/docker/Dockerfile` for more details).


## Set up a new MicroService

Just run the commands:

```bash
$ docker build . -t django_service_wizard
$ docker run -it -u $(id -u):$(id -g) -v "$(pwd)":/code django_service_wizard
```

## Development

Build the docker image:

```bash
docker-compose build
```

Run the tests:

```bash
docker-compose run --entrypoint 'python -m unittest discover' --rm django_service_wizard
```
