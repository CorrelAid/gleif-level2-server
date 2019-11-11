# gleif-level2-server

Server backend for [https://github.com/CorrelAid/gleif-level2-client](https://github.com/CorrelAid/gleif-level2-client).

## Prerequisites for docker-compose

you need a `data` directory with the following files:

- `gleif_lei.csv` (*LEI-CDF*)
- `gleif_rr.csv` (*RR-CDF*)

If you're on Linux, you can use the `data/download.sh` script, for Mac users there is the `data/download_mac.sh` script. They are to be executed in the `data` directory. Both scripts will download the current files from the [GLEIF website](https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy/#/) and remove most of the columns from the `lei` dataset in order to make it small enough for most local RAMs.  
If you're on Windows operating system, you'll need to [download the files manually](https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy/#/) and find a way to reduce the file size of the `lei` dataset.

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

```
docker-compose build
```

#### test

run the tests within a docker container:

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


### logs 

```
docker-compose logs -f
```

## server

For development purposes, we had a server / virtual machine in the Azure cloud. Things should work similarly on your server.

### clone repository to your server

```
git clone git@github.com:CorrelAid/gleif-level2-server.git
```

or

```
git clone https://github.com/CorrelAid/gleif-level2-server.git
```

depending on your GitHub authentication preferences.


### build docker images

```
docker-compose build 
```

### start stack

```
docker-compose up -d
```

### logs 

```
docker-compose logs -f
```


### stop stack

```
docker-compose down
```
