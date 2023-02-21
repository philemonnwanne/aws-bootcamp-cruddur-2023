# Week 1 — App Containerization

## Containerize the Frontend

To containerize the frontend do the following

Switch to the frontend directory amd create a dockerfile

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
