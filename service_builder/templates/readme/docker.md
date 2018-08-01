
## Development

Build the image:

```
$ docker-compose -f docker-compose-dev.yml build
```

Give execute permissions to the entrypoint:

```
$ chmod +x docker-entrypoint.sh
```

Run the web server:

```
$ docker-compose -f docker-compose-dev.yml up
```

Open your browser with URL `http://localhost:8080`.
For the admin panel `http://localhost:8080/admin`
(user: `admin`, password: `admin`).
