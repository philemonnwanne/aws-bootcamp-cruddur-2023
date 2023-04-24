<p align=right> 
<a href="https://gitpod.io/#https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023">
  <img
    src="https://img.shields.io/badge/Contribute%20with-Gitpod-908a85?logo=gitpod"
    alt="Contribute with Gitpod"
    style="text-align: right"
  />
</a>
</p>

# Week 5 — DynamoDB and Serverless Caching

## Required Homework/Tasks

## Automate Database Workflow

While in the backend directory create the folder `bin` create three new files in the `bin/ddb` directory

```bash
touch /bin/ddb/list-tables \
      /bin/ddb/drop \
      /bin/ddb/schema-load \
      /bin/ddb/seed
```

Make the files executable

```bash
chmod 744 bin/ddb/*
```

### Load Database Schema

We will create a new python script `bin/ddb/schema-load` with the following content

```bash
#!/usr/bin/env python3

import boto3
import sys

attrs = {
    'endpoint_url': 'http://localhost:8000',
}

if len(sys.argv) == 2:
    if "prod" in sys.argv[1]:
        attrs = {}

dynamodb = boto3.client('dynamodb',**attrs)

table_name = 'cruddur-message'

response = dynamodb.create_table(
    TableName=table_name,
    AttributeDefinitions=[
        {
            'AttributeName': 'pk',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'sk',
            'AttributeType': 'S'
        },
    ],
    KeySchema=[
        {
            'AttributeName': 'pk',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'sk',
            'KeyType': 'RANGE'
        },
    ],
    BillingMode='PROVISIONED',
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

print(response) 

```

We will make it executable:

```bash
chmod 744 bin/ddb/schema-load
```

To execute the script:

```bash
./bin/ddb/schema-load
```

### List Tables

We will create a new bash script `bin/ddb/list-tables` with the following content

```bash
# Script compatible with both zsh and bash shells
#!/usr/bin/env bash

if [ "$1" = "prod" ]; then
  ENDPOINT_URL=""
  echo "Running in production!!! mode"
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
  echo "Running in development!!! mode"
fi

aws dynamodb list-tables $ENDPOINT_URL
```

We will make it executable:

```bash
chmod 744 bin/ddb/list-tables
```

To execute the script:

```bash
./bin/ddb/list-tables
```