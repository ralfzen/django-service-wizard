
## Development

Build the image:

```bash
docker-compose build
```

Run the web server:

```bash
docker-compose up
```

Open your browser with URL `http://localhost:8080`.
For the admin panel `http://localhost:8080/admin`
(user: `admin`, password: `admin`).

Run the tests:

```bash
docker-compose run --entrypoint '/usr/bin/env' --rm {{ name_project }} bash scripts/run-tests.sh
```
