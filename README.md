# MMIB-Message-Submodule
Message Submodule implementation for the microservices-based application MMIB. 
This is the source code of Message in a Bottle application, self project of *Advanced Software Engineering* course,
University of Pisa.



## Team info

- The *squad id* is **10**
- The *team leader* is Giuseppe Crea

#### Members

| Name and Surname  | Email |
| ----------------  | ----- |
|Giuseppe Crea      |g.crea2@studenti.unipi.it       |
|Francesco Venturini|f.venturini12@studenti.unipi.it|
|Ivan Sarno         |       |
|Francesco Gargiulo |       |
|                   |       |

# Swagger generated server

## Overview
This server was generated by the [swagger-codegen](https://github.com/swagger-api/swagger-codegen) project. By using the
[OpenAPI-Spec](https://github.com/swagger-api/swagger-core/wiki) from a remote server, you can easily generate a server stub.  This
is an example of building a swagger-enabled Flask server.

This example uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requirements
Python 3.5.2+

## Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.dev.txt
python3 -m message_server
```

and open your browser to here:

```
http://localhost:5002//ui/
```

Your Swagger definition lives here:

```
http://localhost:5002//swagger.json
```

To launch the integration tests, use tox:
```
sudo pip install tox
tox
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t message_server .

# starting up a container
docker run -p 5002:5002 message_server
```

## Testing

Start a redis server on localhost:6379. This is needed to test the celery calls.
Place yourself in the home directory of this project and run the command

```
tox
```

This will run pytest and return coverage data.

## CI

Travis.ci is currently refusing new builds from all accounts in our team. Thus, no CI pipeline was set up.