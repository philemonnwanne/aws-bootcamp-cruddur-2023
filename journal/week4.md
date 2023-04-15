<p align=right> 
<a href="https://gitpod.io/#https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023">
  <img
    src="https://img.shields.io/badge/Contribute%20with-Gitpod-908a85?logo=gitpod"
    alt="Contribute with Gitpod"
    style="text-align: right"
  />
</a>
</p>

# Week 4 — Postgres and RDS

## Required Homework/Tasks

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

Accessing the postgres container and running an underlying SQL command

```bash
psql -U postgress --host localhost
```

```sql
CREATE DATABASE cruddur;
```

### Delete Database


Using the command line

```bash
dropdb cruddur -h localhost -U postgres
```

Accessing the postgres container and running an underlying SQL command

```bash
psql -U postgress --host localhost
```

```sql
DROP DATABASE cruddur;
```

### Import Database Script

We will create a new SQL file called `schema.sql` and place it in `backend-flask/db`

#### add UUID extension

We are going to have postgres generate `UUIDs`. We will need to use an extension called: `uuid-ossp`

Add this 👇🏾 to the `schema.sql` file

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Import database schema

Make sure you are in the `backend` directory before running this

```bash
psql cruddur < db/schema.sql -h localhost -U postgres
```

### Passwordless Login

To enable a `passwordless` login to postgres export the following env variable

Sample `connection url format` for postgres

```bash
postgresql://[user:[password]@][netloc]:[port][/dbname][?param1=value1&...]
```

For `local` environment

```bash
export CONNECTION_URL="postgresql://postgres:[password]@127.0.0.1:5432/cruddur"
```

For `gitpod` environment

```bash
gp env CONNECTION_URL="postgresql://postgres:[password]@127.0.0.1:5432/cruddur"
```

`Note:` Remember to pass the right username, password, host etc. Then run `psql $CONNECTION_URL` to login without a password


### Production(RDS) Connection Url Format

For `local` environment

```bash
export PROD_CONNECTION_URL="postgresql://cruddurroot:[password]@[aws-db-endpoint]:5432/cruddur"
```

For `gitpod` environment

```bash
export PROD_CONNECTION_URL="postgresql://cruddurroot:[password]@[aws-db-endpoint]:5432/cruddur"
```

```bash
gp env PROD_CONNECTION_URL="postgresql://cruddurroot:[password]@[aws-db-endpoint]:5432/cruddur"
```

## Automate Database Workflow

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
 
### Update Bash scripts for Prod & Dev Env

```bash
if [ "$1" = "prod" ]; then
  echo "Running in production!!! mode"
else
  echo "Running in development!!! mode"
fi
```

### Make Prints Nicer

We can make prints for our shell scripts coloured so we can see what we're doing

[how-to-change-the-output-color-of-echo-in-linux](https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux)

```ruby
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"
```

### Create/Delete Tables

Add this 👇🏾 to the `schema.sql` file

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

We will create a new bash script `bin/db-connect` with the following content

```bash
# Script compatible with both zsh and bash shells
#!/usr/bin/env bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-connect"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  URL=$PROD_CONNECTION_URL
  echo "Connected to the Production DATABASE!!!"
else
  URL=$DEV_CONNECTION_URL
  echo "Connected to the Development DATABASE!!!"
fi

psql $URL
```

We will make it executable:

```bash
chmod 744 bin/db-connect
```

To execute the script:

```bash
./bin/db-connect
```

### Add sample data to our Database

We will create a new file `db/seed.sql` with the following content

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

### Seed the Database

We will create a new script `bin/db-seed` with the following content

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
  URL=$PROD_CONNECTION_URL
  echo "Running in production!!! mode"
else
  URL=$DEV_CONNECTION_URL
  echo "Running in development!!! mode"
fi

psql $URL cruddur < $seed_path && echo "Database seeded Successfully" 
```

We will make it executable:

```bash
chmod 744 bin/db-seed
```

To execute the script:

```bash
./bin/db-seed
```


### See what connections we are using

We will create a new script `bin/db-sessions` with the following content

```bash
# Script compatible with both zsh and bash shells
#!/usr/bin/env bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-session"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  URL=$PROD_CONNECTION_URL
  echo "Running in production!!! mode"
else 
  URL=$DEV_CONNECTION_URL
  echo "Running in development!!! mode"
fi

NO_DB_URL=$(sed 's/\/cruddur//g' <<< "$URL")
psql $NO_DB_URL -c "select pid as process_id, \
       usename as user,  \
       datname as db, \
       client_addr, \
       application_name as app,\
       state \
from pg_stat_activity;"
```

We will make it executable:

```bash
chmod 744 bin/db-sessions
```

To execute the script:

```bash
./bin/db-sessions
```

### Automate database setup (for local... dev mode only ⚠️❗️)

We will create a new script `bin/db-setup` with the following content

```bash
# Script compatible with both zsh and bash shells
#!/usr/bin/env bash
-e # stop if it fails at any point

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-setup"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

bin_path="$(realpath .)/bin"

source "$bin_path/db-drop"
source "$bin_path/db-create"
source "$bin_path/db-schema-load"
source "$bin_path/db-seed"
```

We will make it executable:

```bash
chmod 744 bin/db-setup
```

To execute the script:

```bash
./bin/db-setup
```

### Install Postgres Driver

We will add the following to our `requirements.txt`

```txt
...
psycopg[binary]
psycopg[pool]
```

Now run

```bash
pip install -r requirements.txt
```

### DB Object and Connection Pool

We will create a new file `lib/db.py` with the following content

```python
from psycopg_pool import ConnectionPool
import os # to load env vars

def query_wrap_object(template):
  sql = f"""
  (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
  {template}
  ) object_row);
  """
  return sql

def query_wrap_array(template):
  sql = f"""
  (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
  {template}
  ) array_row);
  """
  return sql

connection_url = os.getenv("CONNECTION_URL")
pool = ConnectionPool(connection_url)
```

We need to set the `env var` for our backend-flask application

```yaml
  backend-flask:
    environment:
      CONNECTION_URL: "${DEV_CONNECTION_URL}"
```

### Run a query in Home Activities

Add the following to `home_activities.py`

```python
from lib.db import pool
```

In our home activities we will replace our mock endpoint with real api call

```python
with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
        # this will return a tuple
        # the first field being the data
        json = cur.fetchall()
return json[0]
```

The new `home_activities.py` should now look like this 👇🏾

```python
from datetime import datetime, timedelta, timezone
# from opentelemetry import trace
from lib.db import pool, query_wrap_array

# tracer = trace.get_tracer("home_activities")

class HomeActivities:
  def run(cognito_user_id=None):
    # logger.info("HomeActivities")
    # with tracer.start_as_current_span("home_activities_mock_data"):
      # span = trace.get_current_span()
    # now = datetime.now(timezone.utc).astimezone()
    # span.set_attribute("app.now", now.isoformat())

    sql = query_wrap_array("""
    SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
    """)

    with pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(sql)
        # this will return a tuple
        # the first field being the data
        json = cur.fetchone()
    return json [0]
    # span.set_attribute("app.result_length", len(results))
```

### Connect to RDS via Gitpod

In order to connect to the RDS instance we need to provide our Gitpod IP and whitelist for inbound traffic on port `5432`.

```bash
GITPOD_IP=$(curl ifconfig.me)
```

We'll create an inbound rule for Postgres `(5432)` and provide the `GITPOD ID`.

We'll get the security group `rule id` so we can easily modify it in the future from the terminal here in Gitpod.

For gitpod environment

```bash
export DB_SG_ID="sg-xxxxxxxx"
gp env DB_SG_ID="sg-xxxxxxxx"

export DB_SG_RULE_ID="sgr-xxxxxxxx"
gp env DB_SG_RULE_ID="sgr-xxxxxxxx"
```

Whenever we need to update our security groups we can do this for access.

```bash
aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32,Description=RDS_Access_Phil}"
```

[modify-security-group-rules-aws](https://docs.aws.amazon.com/cli/latest/reference/ec2/modify-security-group-rules.html#examples)

To automate the process above

Then we will create a new script `bin/db-sg-rule-mod` with the following content

```bash
# Script compatible with both zsh and bash shells
# Auto detect OS and apply configurations based on returned data
#!/usr/bin/env bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-sg-rule-mod"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

export OS1=$(lsb_release -is 2>/dev/null)
export OS2=$(sw_vers --productName 2>/dev/null)

if [ "$OS1" = "Ubuntu" ]; then
  export GITPOD_IP=$(curl ifconfig.me)
  EXT_IP=$GITPOD_IP
  echo "This is a ${OS1} environment!!!"
else
  export MACHINE_IP=$(curl -s http://ipecho.net/plain; echo)
  EXT_IP=$MACHINE_IP
  echo "This is a ${OS2} environment!!!"
fi

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$EXT_IP/32,Description=RDS_Access_Phil}"
```

Remember to export the following `env vars`

```bash
DB_SG_ID
DB_SG_RULE_ID
```

We will make it executable:

```bash
chmod 744 bin/db-sg-rule-mod
```

To execute the script:

```bash
./bin/db-sg-rule-mod
```

### Update Gitpod IP on new env var

We'll add a command step to update rds secgrp IP on env var change

```yaml
- name: update-rds-secgrp-IP
  command: |
    export GITPOD_IP=$(curl ifconfig.me)
    source "$THEIA_WORKSPACE_ROOT/backend-flask/bin/db-update-sg-rule"
```

### Setup Cognito post confirmation lambda

#### Edit backend/db/schema.sql

In the `schema.sql` file, add the email parameter to the users table.

```sql
CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text NOT NULL,
  handle text NOT NULL,
  email text NOT NULL, -- insert this line
  cognito_user_id text NOT NULL,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

#### Create the handler function

- Create a lambda function in the same vpc as the rds instance Python 3.8
- Add a layer for `psycopg2` with one of the below methods for development or production

ENV variables needed for the lambda environment

```bash
PG_HOSTNAME='cruddur-db-instance.xxxxxxx.<aws-region>.rds.amazonaws.com'
PG_DATABASE=''
PG_USERNAME=''
PG_PASSWORD=''
```

The function

```python
import os
import psycopg2

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print('userAttributes')
    print(user)

    user_display_name     = user['name']
    user_email            = user['email']
    user_handle           = user['preferred_username']
    user_cognito_id       = user['sub']
    try:
      sql = f"""
        INSERT INTO  public.users (
        display_name,
        email,
        handle, 
        cognito_user_id
        )
        VALUES (
          '{user_display_name}', 
          '{user_email}',
          '{user_handle}',
          '{user_cognito_id}'
        )
      """
      conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
      cur = conn.cursor()
      cur.execute(sql)
      conn.commit() 

    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
    finally:
      if conn is not None:
        cur.close()
        conn.close()
        print('Database connection closed.')
            
    return event
```

Then do the following 👇🏾

- Copy the lamdba code in `aws/lambdas/cruddur-post-confirmation.py` to the lambda code source in aws and click on `deploy`
- Click on the `configurations` tab to add an environment variable for the `CONNECTION_URL` then save

### Development

[aws-psycopg2](https://github.com/AbhimanyuHK/aws-psycopg2)

This is a custom compiled psycopg2 C library for Python. Due to AWS Lambda missing the required PostgreSQL libraries in the AMI image, we needed to compile psycopg2 with the PostgreSQL libpq.so library statically linked libpq library instead of the default dynamic link.

`Easiest Method`

Some precompiled versions of this layer are available publicly on AWS freely to add to your function by ARN reference.

[psycopg2-lambda-layer](https://github.com/jetbridge/psycopg2-lambda-layer)

`Note:` Just go to the Layers + in the lambda function console and add a reference for your region, in my case `us-east-1`

`arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py38:2`

Alternatively you can create your own development layer by downloading the psycopg2-binary source files from `https://pypi.org/project/psycopg2-binary/#files`

- Download the package for the lambda runtime environment: [psycopg2_binary-2.9.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl](https://files.pythonhosted.org/packages/36/af/a9f06e2469e943364b2383b45b3209b40350c105281948df62153394b4a9/psycopg2_binary-2.9.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl)

- Extract to a folder, then zip up that folder and upload as a new lambda layer to your AWS account

### Production

Follow the instructions on `https://github.com/AbhimanyuHK/aws-psycopg2` to compile your own layer from postgres source libraries for the desired version.

### Add the function to Cognito

- Click on your user pool in the cognito console
- Under the `user pool properties` click on `Add Lambda trigger`
- Choose Sign-up then then `Add Lambda trigger`
- In the `Assign Lambda function` dropdown, select the post confirmation lambda function created earlier
- Then click `Add Lambda trigger`
