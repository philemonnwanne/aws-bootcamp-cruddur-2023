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

## Homework Challenges [Done](#Homework-Challenges)
- [x] [Run the Dockerfile CMD as an external script]()
- [x] [Push and tag a image to DockerHub]()
- [x] [Use multi-stage building for a Dockerfile build]()
- [x] [Implement a healthcheck in the V3 Docker compose file]()
- [x] [Research best practices of Dockerfiles and attempt to implement it in your Dockerfile]()
- [x] [Learn how to install Docker on your localmachine and get the same containers running outside of Gitpod / Codespaces]()
- [x] [Launch an EC2 instance that has docker installed, and pull a container to demonstrate you can run your own docker processes]()



### To containerize the project we will do the following

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
      

# Docker Network
networks:
  crudder-network:
    driver: bridge
```

### Link to my Open API documentation: https://crudder.readme.io/docs


# Homework Challenges

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

### Add Postgres Service

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

Postgres Connection Made

![postgres_local](https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023/blob/main/journal/images/week1/postgres_local.png)

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

`Note:` Remember to update the `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY` in our `.env` file

Dynamodb Connection Made

![dynamodb_local](https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023/blob/main/journal/images/week1/dynamodb_local.png)


## Docker On AWS EC2
Steps to recreate
- Launch an ubuntu ec2 instance
- login to the instance via ssh
- install the docker engine here [docker engine](https://docs.docker.com/engine/install/ubuntu/)
- clone the project repo fron github and rename it to `crudder`

```bash
git clone https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023.git crudder
```
Switch to the project directory and into the `frontend-react-js` directory

```bash
cd crudder/frontend-react-js
```

Create a Dockerfile
```bash
nano Dockerfile
```

Paste the following into the Dockerfile
```Dockerfile
# build stage
FROM node:alpine as build

WORKDIR /frontend-react-js

COPY . .

RUN rm -rf node_modules \
    && npm install \
    && npm run build

# production stage
FROM nginx:alpine

# copy everything in the build stage into the final stage
COPY --from=build /frontend-react-js/build /usr/share/nginx/html
```

![crudder_instance](https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023/blob/main/journal/images/week1/crudder_ubuntu.png)


## Health Check
Add the following lines to the compose file created earlier to implement a health check

```yaml
version: "3.8"

services:
# Frontend Service
  frontend:
    environment:
      REACT_APP_BACKEND_URL: "http://localhost:4567"
    build: ./frontend-react-js
    container_name: frontend
    ports:
      - "3000:3000"
    healthcheck:
      test: npm --version || exit 1
      interval: 30s
      retries: 5
      start_period: 5s
      timeout: 10s
    volumes:
      - ./frontend-react-js:/frontend-react-js
      - /frontend-react-js/node_modules
    networks:
      - crudder-network

# Backend Service
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

# Database Service[Postgres]
  postgres-db:
    image: postgres:alpine
    restart: always
    environment:
      POSTGRES_USER: philemonnwanne
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
    container_name: postgres-db
    ports:
      - '5432:5432'
    volumes:
      - db:/var/lib/postgresql/data

  dynamodb-local:
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal

# Docker Networks
networks:
  crudder-network:
    driver: bridge

# Docker Volumes
volumes:
  db:
    driver: local
```

#### Dockerfile Output

![health_check](https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023/blob/main/journal/images/week1/health_check_1.png)



## Best Dockerfile Practices Researched and Implemented

- Used explicit and deterministic Docker base image tags
- Installed only production dependencies in the Node and Python based Docker image
- Optimized Node.js tooling for production
- Used small sized images to reduce attack surface area
- Did not run containers as root where possible
- Found and fixed security vulnerabilities in my docker image using Snyk
- Implemented multi-stage builds
- Used `.env` to handle secrets and made sure not to push them to version control
- Kept unnecessary files out of the Docker images
- Mounted secrets into the Docker build image
- Optimized caching for image layers when building an image
