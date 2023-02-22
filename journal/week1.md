<p align=right> 
<a href="https://gitpod.io/#https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023">
  <img
    src="https://img.shields.io/badge/Contribute%20with-Gitpod-908a85?logo=gitpod"
    alt="Contribute with Gitpod"
    style="text-align: right"
  />
</a>
</p>

# Week 1 — App Containerization

To containerize the project we will do the following
- clone the project repo to our local machine 
- make sure both apps are running fine locally 
- create a Dockerfle for each one

## Containerize the Frontend

Switch to the frontend directory and create a dockerfile
```bash
cd frontend-react-js

nano Dockerfile
```

Populate the Dockerfile you just created with the following instructions
```dockerfile
FROM node:16.18

ENV PORT=3000

COPY . /frontend-react-js

WORKDIR /frontend-react-js

RUN rm -rf node_modules \
    && npm install

EXPOSE ${PORT}

CMD ["npm", "start"]
```


## Containerize the Backend

To containerize the backend do the following

Switch to the backend directory and create a dockerfile
```bash
cd backend-flask

nano Dockerfile
```

Populate the Dockerfile you just created with the following instructions
```dockerfile
FROM python:3.10-slim-buster

WORKDIR /backend-flask

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_ENV=development \
    FRONTEND_URL="*" \
    BACKEND_URL="*" \
    PORT=4567

EXPOSE ${PORT}

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
```

Now that we have the two applications containerized and working as we want, it's time to orchestrate the containers

## Orchestrate the Containers

Make sure you are in the project root folder and create a `docker-compose` file

```yaml
version: "3.8"

services:
# Frontend Application
  frontend:
    environment:
      REACT_APP_BACKEND_URL: "http://localhost:4567"
    build: ./frontend-react-js
    container_name: frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend-react-js:/frontend-react-js
    networks:
      - crudder-network

# Backend Application
  backend:
    environment:
      FRONTEND_URL: "http://localhost:3000"
      BACKEND_URL: "http://localhost:4567"
    build: ./backend-flask
    container_name: backend
    ports:
      - "4567:4567"
    volumes:
      - ./backend-flask:/backend-flask
    networks:
      - crudder-network
      
  healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost"]
  interval: 1m30s
  timeout: 10s
  retries: 3
  start_period: 40s

# Docker Network
networks:
  crudder-network:
    driver: bridge
```


## Multistage Build

Multistage build involves utilising multiple stages in a Dockerfile, while we build an image in order to significantly reduce the size of our docker image. In the end we’ll have an image that does the exact same thing but is almost 10 times smaller in size! The way we can achieve this is by keeping only the actual files needed for production and leaving unnecesary ones behind in the build stage. e.g (leaving behind tools we use for building the image).

For this project we will have to redefine the Docker file used earlier for the Frontend app as it has more room for optimisation

Switch to the frontend directory and edit the previous Dockerfile

```bash

cd frontend-react-js

nano Dockerfile
```

Now edit the Dockerfile to look like the following

```dockerfile
# build stage
FROM node:16.18 as build

WORKDIR /frontend-react-js

COPY . /frontend-react-js

RUN rm -rf node_modules \
    && npm install \
    && npm run build

# production stage
FROM nginx:alpine

# copy the final output of the build stage into the final stage
COPY --from=build /frontend-react-js/build /usr/share/nginx/html
```

## Tag and push a image to DockerHub

### Tag an image

```bash
docker tag imagename philemonnwanne/imagename:version1.0
```

### Push the image
```bash
docker image push philemonnwanne/imagename:version1.0
```


## Run Postgres Container

Now we're going to add a postgres container to our initial compose file and make sure it works locally

### Create `env`

First of go into the project root directory and create an `env` file

```bash
nano .env
```

Poulate the env file with the folowing key:pair value and remember not to commit it to version control

```env
POSTGRES_PASSWORD="your password goes in here"
```

### Add Dynamodb Service

Then we are going to add a new service for the postgres database to our compose file

- Add the following code to the `docker-compose.yml` file.

```yaml
version: "3.8"

services:
...
...
      
 # Database Service[Postgres]
  db:
    image: postgres:alpine
    restart: always
    environment:
      POSTGRES_USER: philemonnwanne
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
    ports:
      - '5432:5432'
    volumes:
      - db:/var/lib/postgresql/data
    networks:
      - crudder-network
      
 # Docker Network
networks:
  crudder-network:
    driver: bridge

# Docker Volumes
volumes:
  db:
    driver: local
```

## Run DynamoDB local Container

To install and run DynamoDB local with Docker compose;

- Add the following code to the `docker-compose.yml` file.

```yaml
version: "3.8"

services:
...
...
...

# Database Service[dynamodb-local]
  dynamodb-local:
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal

# AWS-CLI Service [To test dynamodb fucntionality]
  app-node:
    depends_on:
      - dynamodb-local
    image: amazon/aws-cli
    container_name: app-node
    ports:
     - "8080:8080"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
    command:
      dynamodb describe-limits --endpoint-url http://dynamodb-local:8000 --region us-east-1
```

