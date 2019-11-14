# GLEIF Level-2 Visualization (Server)

The code was written during a hackathon between [GLEIF](https://www.gleif.org/) and [CorrelAid](https://www.correlaid.org). :rocket: The goal of the project was to visualize relational data between legal entites that are registered at GLEIF. More information about the open data available at GLEIF can be found here: [https://www.gleif.org/en/lei-data/access-and-use-lei-data](https://www.gleif.org/en/lei-data/access-and-use-lei-data). Furthermore, an introductory blog post can be found here: [https://correlaid.org/en/blog/gleif-hackathon/](https://correlaid.org/en/blog/gleif-hackathon/).

This is the server of the project the client can be found here: [https://github.com/CorrelAid/gleif-level2-client](https://github.com/CorrelAid/gleif-level2-client).

## Current Limitations

Due to the nature of hackthons the current version of the tool includes the following limitations:

- The documentation of the code might be partially incomplete. If you come across an issue please file an issue within this repository.
- The backend reacts quiet slowly due to the design decisions.
- Some edge-cases are not handeled.

## License

The tool is licensed under CC0.

## Prerequisites 

You need a `data` directory with the following files:

- `gleif_lei.csv` (*LEI-CDF*)
- `gleif_rr.csv` (*RR-CDF*)

If you're on Linux, you can use the `data/download.sh` script, for Mac users there is the `data/download_mac.sh` script. They are to be executed in the `data` directory. Both scripts will download the current files from the [GLEIF website](https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy/#/) and remove most of the columns from the `lei` dataset in order to make it small enough for most local RAMs.  
If you're on Windows operating system, you'll need to [download the files manually](https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy/#/) and find a way to reduce the file size of the `lei` dataset.


## API docs

You can find the Swagger API docs under [http://localhost:8000/docs](http://localhost:8000/docs) after you have started the app either directly on your machine or with docker (see below).


## Local development

### without docker

#### run

e.g. in conda / venv:
-> with reload enabled

```
uvicorn app:api --reload --root-path src
```

This makes the API available under [http://localhost:8000/](http://localhost:8000/).

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

This makes the API available under [http://localhost:8000/](http://localhost:8000/).

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

This makes the API available under [http://localhost:8000/](http://localhost:8000/) on your server. Configure a reverse proxy (e.g. [Nginx](https://www.nginx.com/)) to make the API available to other machines. 


### logs 

```
docker-compose logs -f
```


### stop stack

```
docker-compose down
```
