# sample-service

An example MicroService repository for the Humanitec Platform Walhall

## Set up a new MicroService

Build the docker image:

```bash
docker-compose -f docker-compose.yml build
```

Then run the created image:

```bash
docker-compose -f docker-compose.yml run --rm sample_service
```

## Development

Build the docker image:

```bash
docker-compose -f docker-compose.yml build
```

Run the tests:

```bash
docker-compose -f docker-compose.yml run --entrypoint 'python -m unittest discover .' --rm sample_service
```

To run the image with pdb debugging support:

```bash
docker-compose -f docker-compose.yml run --service-ports --rm sample_service
```
