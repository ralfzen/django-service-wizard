[![Build Status](http://drone.humanitec.io/api/badges/Humanitec/django-service-wizard/status.svg)](http://drone.humanitec.io/Humanitec/django-service-wizard)

# django-service-wizard

A Django (Micro)Service wizard for the Humanitec Platform Walhall. This will
help you to setup your a project from scratch.

## Set up a new MicroService

Build the docker image:

```bash
docker-compose -f docker-compose.yml build
```

Then run the created image:

```bash
docker-compose -f docker-compose.yml run --rm django_service_wizard
```

## Development

Build the docker image:

```bash
docker-compose -f docker-compose.yml build
```

Run the tests:

```bash
docker-compose -f docker-compose.yml run --entrypoint 'python -m unittest discover .' --rm django_service_wizard
```

To run the image with pdb debugging support:

```bash
docker-compose -f docker-compose.yml run --service-ports --rm django_service_wizard
```
