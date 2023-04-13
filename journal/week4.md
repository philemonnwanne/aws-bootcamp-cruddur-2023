# Week 4 — Postgres and RDS

## Provision an RDS Instance

You can export sensitive details as environment variables or use any other convenient secrets handler. For my use case I have set the following env variables

```bsh
$RDS_ROOT_USER
$RDS_ROOT_PASS
$RDS_DB_NAME
$RDS_DB_PORT
$RDS_ENGINE
$RDS_ENGINE_VERSION
```

To launch our RDS db into a particular vpc we have to specify the `--db-subnet-group-name` parameter.
But for this to work we need to have an already existing DB subnet group, to create one run the following command, remember to reference your own subnet ids

```bash
aws rds create-db-subnet-group \
    --db-subnet-group-name cruddur_db_subnet_group \
    --db-subnet-group-description "cruddur DB subnet group" \
    --subnet-ids '["subnet-0a1dc4e1a6f123456","subnet-070dd7ecb3aaaaaaa"]'
```

Now run the following command to create an `RDS instance` on AWS

```bash
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine $RDS_ENGINE \
  --engine-version  $RDS_ENGINE_VERSION \
  --master-username $RDS_ROOT_USER \
  --master-user-password $RDS_ROOT_PASS \
  --allocated-storage 20 \
  --db-subnet-group-name cruddur_db_subnet_group \
  --backup-retention-period 0 \
  --port $RDS_DB_PORT \
  --no-multi-az \
  --db-name $RDS_DB_NAME \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```

If the above command is successful you will get a similar `json` ouput

```json
{
    "DBSubnetGroup": {
        "DBSubnetGroupName": "cruddur_db_subnet_group",
        "DBSubnetGroupDescription": "cruddur DB subnet group",
        "VpcId": "vpc-0609559736befeb7f",
        "SubnetGroupStatus": "Complete",
        "Subnets": [
            {
                "SubnetIdentifier": "subnet-0d2543173bfc71159",
                "SubnetAvailabilityZone": {
                    "Name": "us-east-1a"
                },
                "SubnetOutpost": {},
                "SubnetStatus": "Active"
            },
            {
                "SubnetIdentifier": "subnet-0628decec8bc21a96",
                "SubnetAvailabilityZone": {
                    "Name": "us-east-1b"
                },
                "SubnetOutpost": {},
                "SubnetStatus": "Active"
            }
        ],
        "DBSubnetGroupArn": "arn:aws:rds:us-east-1:xxxxxxx:subgrp:cruddur_db_subnet_group",
        "SupportedNetworkTypes": [
            "IPV4"
        ]
    }
}
```

To connect to a local postgres db

```bash
psql -U postgress --host localhost
```

### Create Database

There are a few ways to create a database, some of which are


Using the command line

```bash
createdb cruddur -h localhost -U postgres
```

Accessing the postgres container and using an underlying SQL command

```bash
psql -U postgress --host localhost
```

```bash
CREATE database cruddur;
```

### Delete Database


Using the command line

```bash
dropdb cruddur -h localhost -U postgres
```

Accessing the postgres container and using an underlying SQL command

```bash
psql -U postgress --host localhost
```

```bash
DROP database cruddur;
```

### Import Database Script

We'll create a new SQL file called `schema.sql` and place it in `backend-flask/db`

#### Add UUID Extension

We are going to have Postgres generate out `UUIDs`. We'll need to use an extension called:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

Add this to the `schema.sql` file

### The command to import

Make sure you are in the `backend` directory before running this

```bash
psql cruddur < db/schema.sql -h localhost -U postgres
```


### Passwordless Login

To enable a `passwordless` login to postgres export the following env variable

#### Connection url format for postgres

```bash
postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
```

```bash
export CONNECTION_URL="postgresql://postgres[:password]@127.0.0.1:5432/cruddur"
```

For `gitpod` environments use

```bash
gp env CONNECTION_URL="postgresql://postgres[:password]@127.0.0.1:5432/cruddur"
```

Remember to pass the right username, password, host etc. Then run `psql $CONNECTION_URL` to login without a password


#### Production(RDS) Connection URL

Locally

```bash
export PROD_CONNECTION_URL="postgresql://cruddurroot[:password]@[aws-db-endpoint]:5432/cruddur"
```

For `gitpod` environments use

```bash
gp env PROD_CONNECTION_URL="postgresql://cruddurroot[:password]@[aws-db-endpoint]:5432/cruddur"
```

### Automate Database Workflow

While in the backend directory create the folder `bin` this will hold all the shell scripts for working on our database

create three new files in the `bin` directory

```bash
touch /bin/db-create \
      /bin/db-drop \
      /bin/db-schema-load
```

Make the files executable

```bash
chmod 744 bin/*
```
 
### Update Bash scripts for Prod & Dev Mode

```bash
if [ "$1" = "prod" ]; then
  echo "Running in production!!! mode"
else
  echo "Running in development!!! mode"
fi
```

### Make prints nicer

We we can make prints for our shell scripts coloured so we can see what we're doing:

[](https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux)

```ruby
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"
```

### Create/Delete Tables

```sql
DROP TABLE IF EXISTS public.users;

CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);

DROP TABLE IF EXISTS public.activities;

CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

### Connect to the Database

We'll create a new bash script `bin/db-connect` with the following content

```bash
# Script compatible with both zsh and bash shells
#!/usr/bin/env bash

if [ "$1" = "prod" ]; then
  echo "Connected to the Production DATABASE!!!"
  URL=$PROD_CONNECTION_URL
else
  echo "Connected to the Development DATABASE!!!"
  URL=$DEV_CONNECTION_URL
fi

psql $URL
```

We'll make it executable:

```bash
chmod 744 bin/db-connect
```

To execute the script:

```bash
./bin/db-connect
```

### Seed the Database

We'll create a new bash script `bin/db-seed` with the following content

```bash
# Script compatible with both zsh and bash shells
#!/usr/bin/env bash

# seed_path="db/seed.sql"

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

seed_path="$(realpath .)/db/seed.sql"

if [ "$1" = "prod" ]; then
  echo "Running in production!!! mode"
  URL=$PROD_CONNECTION_URL
else
  echo "Running in development!!! mode"
  URL=$DEV_CONNECTION_URL
fi

psql $URL cruddur < $seed_path && echo "Database seeded Successfully" 
```

#### Add sample data to our DB

We'll create a new file `db/seed.sql` with the following content

```sql
-- this file was manually created
INSERT INTO public.users (display_name, handle, cognito_user_id)
VALUES
  ('Philemon Nwanne', 'philemonnwanne', 'MOCK'),
  ('Unknown Variable', 'unknownvariable', 'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'philemonnwanne' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )
```

We'll make it executable:

```bash
chmod 744 bin/db-seed
```

To execute the script:

```bash
./bin/db-seed
```

