# App

## Overview

Django web app with Leaflet and SQLite.

## Development

Update the *app* section of the `.env.dev` file.

`DB_NAME` is the path of the sqlite file. If the sqlite file does not exist, it will be created upon initialization. Note that the db/ subdirectory is a mounted volume (see "docker-compose.yml").  The remaining variables prefixed with `DJANGO_` are admin superuser credentials.

```sh
$ make dev-up       # This runs the db migrations
$ make superuser    # Create a superuser for first-time run
```

Develop, update and run tests:

```sh
make test
```

Once we're happy enough with how dev looks like, bring down the dev services:

```sh
make dev-down
```

Apply the changes we've made in dev in our actual apps: modify the `.env` file and run the same sequence of make commands, removing the `dev-` prefixes.
