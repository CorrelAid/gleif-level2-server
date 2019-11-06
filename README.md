# backend

## prerequisites for docker-compose

you need a `data` directory with the following files:

- `gleif_lei.csv`
- `gleif_rr.csv`

If you're on Linux, you can use the `data/download.sh` script, for Mac users there is the `data/download_mac.sh` script. They are to be executed in the `data` directory. Both scripts will download the current files from the GLEIF website and remove most of the columns from the `lei` dataset in order to make it small enough for most local RAMs.  
If you're on Windows operating system, you'll need to download the files manually and find a way to reduce the file size of the `lei` dataset.

## local development

### without docker

#### run

e.g. in conda / venv:
-> with reload enabled

```
uvicorn src.api.main:app --reload
```

#### test

```
pytest
```

### with docker

#### build

to build the image, run from the root directory (backend):

```
./build_local.sh
```

#### test

run the test within a docker container:

```
./test.sh
```

#### run

to run:

```
docker-compose up
```

or demonized:

```
docker-compose up -d
```

## server

For development purposes, we had a server / virtual machine in the Azure cloud. Things should work similarly on your server.

### clone repository to your server

```
git clone git@gitlab.com:gleif_it/correlaid/backend.git
```

or

```
git clone https://gitlab.com/gleif_it/correlaid/backend.git
```

depending on your setup.

### Login to gitlab registry (optional)

- optionally, if not logged in yet

```
docker login registry.gitlab.com
```

this will ask for your personal gitlab credentials.

In the future, this could be also done with a gitlab deploy token.

### pull from gitlab

```
git pull
```

depending on your git setup, might ask for access token / password or password for SSH key (if there is one).

### update docker images

```
docker-compose pull
```

This will pull the newest version of the docker images from GitLab registry.

alternatively, build docker image locally on the server:

```
./build_local.sh
```

### start stack

```
docker-compose up -d
```

### stop stack

```
docker-compose down
```

### logs

```
docker logs backend_backend_1
```
