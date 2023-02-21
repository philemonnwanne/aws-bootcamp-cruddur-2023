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

# Docker Network
networks:
  crudder-network:
    driver: bridge
```
