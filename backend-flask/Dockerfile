FROM 183066416469.dkr.ecr.us-east-1.amazonaws.com/cruddur-python:3.11.3-alpine

WORKDIR /backend-flask

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_ENV=development \
    FRONTEND_URL="*" \
    BACKEND_URL="*" \
    PORT=4567

EXPOSE ${PORT}

# CMD [ "./init.sh"]
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=4567" ]
