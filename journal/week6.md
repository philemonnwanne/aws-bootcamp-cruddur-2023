<p align=right> 
<a href="https://gitpod.io/#https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023">
  <img
    src="https://img.shields.io/badge/Contribute%20with-Gitpod-908a85?logo=gitpod"
    alt="Contribute with Gitpod"
    style="text-align: right"
  />
</a>
</p>

# Week 6 — Deploying Containers

## Required Homework/Tasks

### Test RDS Connection

While in the backend directory, we will create a new python script `bin/db/test` with the following content.

Add this test script into db so we can easily check our connection from our container.

```python
#!/usr/bin/env python3

import psycopg
import os
import sys

connection_url = os.getenv("CONNECTION_URL")

conn = None
try:
  print('attempting connection')
  conn = psycopg.connect(connection_url)
  print("Connection successful!")
except psycopg.Error as e:
  print("Unable to connect to the database:", e)
finally:
  conn.close()
```

We will make it executable:

```bash
chmod 744 bin/db/test
```

To execute the script:

```bash
./bin/db/test
```

### Implement Health Check for the Backend App

```python
@app.route('/api/health-check')
def health_check():
  return {'success': True}, 200
```

Update `app.py`

```python



```

In the `backend/bin` directory, we will create a new directory `flask` and a script `health-check` with the following content.

```python
#!/usr/bin/env python3

import urllib.request

try:
  response = urllib.request.urlopen('http://localhost:4567/api/health-check')
  if response.getcode() == 200:
    print("[OK] Flask server is running")
    exit(0) # success
  else:
    print("[BAD] Flask server is not running")
    exit(1) # false
# This for some reason is not capturing the error....
#except ConnectionRefusedError as e:
# so we'll just catch on all even though this is a bad practice
except Exception as e:
  print(e)
  exit(1) # false
```

We will make it executable:

```bash
chmod 744 bin/flask/health-check
```

To execute the script:

```bash
./bin/flask/health-check
```

### Create Cloudwatch Logs

We would want to have a general log for our cluster, and also set the retention period to 1 day

```bash
aws logs create-log-group --log-group-name "cruddur-fargate-cluster" \
aws logs put-retention-policy --log-group-name "cruddur-fargate-cluster" --retention-in-days 1
```

### Create Fargate Cluster

```bash
aws ecs create-cluster \
--cluster-name cruddur \
--service-connect-defaults namespace=cruddur
```

### Gaining Access to ECS Fargate Container

Create ECR repo and push image

```sh
aws ecr create-repository \
  --repository-name cruddur-python \
  --image-tag-mutability MUTABLE
```

### Login to ECR

> Always do this before pushing to ECR

```bash
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```

#### Set URL

```sh
export ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"

echo $ECR_PYTHON_URL
```

### For Base-image python

#### Pull Image

```sh
docker pull python:3.11.3-alpine
```

#### Tag Image

```sh
docker tag python:3.11.3-alpine $ECR_PYTHON_URL:3.11.3-alpine
```

#### Push Image

```sh
docker push $ECR_PYTHON_URL:3.11.3-alpine
```

### For Flask

In your flask dockerfile update the from to instead of using DockerHub's python image
you use your own eg.

> remember to put the :latest tag on the end

Create Repo

```sh
aws ecr create-repository \
  --repository-name backend-flask \
  --image-tag-mutability MUTABLE
```

Set URL

```sh
export ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
echo $ECR_BACKEND_FLASK_URL
```

Build Image

```sh
docker build -t backend-flask .
```

Tag Image

```sh
docker tag backend-flask:latest $ECR_BACKEND_FLASK_URL
```

Push Image

```sh
docker push $ECR_BACKEND_FLASK_URL
```

### For Frontend React

Create Repo

```sh
aws ecr create-repository \
  --repository-name frontend-react-js \
  --image-tag-mutability MUTABLE
```

Set URL

```sh
export ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
echo $ECR_FRONTEND_REACT_URL
```

Build Image

```sh
docker build \
--build-arg REACT_APP_BACKEND_URL="https://4567-$GITPOD_WORKSPACE_ID.$GITPOD_WORKSPACE_CLUSTER_HOST" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="ca-central-1_CQ4wDfnwc" \
--build-arg REACT_APP_CLIENT_ID="5b6ro31g97urk767adrbrdj1g5" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```

Tag Image

```sh
docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest
```

Push Image

```sh
docker push $ECR_FRONTEND_REACT_URL:latest
```

If you want to run and test it

```sh
docker run --rm -p 3000:3000 -it frontend-react-js 
```

## Register Task Defintions

### Passing Senstive Data to Task Defintion

Make sure the following are set as environment variables before running the following commands

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- PROD_CONNECTION_URL
- ROLLBAR_ACCESS_TOKEN
- OTEL_EXPORTER_OTLP_HEADERS

[specifying-sensitive-data](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html)

[secrets-envvar-ssm-paramstore](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-ssm-paramstore.html)

```sh
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_ACCESS_KEY_ID" --value $AWS_ACCESS_KEY_ID
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY" --value $AWS_SECRET_ACCESS_KEY
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/CONNECTION_URL" --value $PROD_CONNECTION_URL
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" --value $ROLLBAR_ACCESS_TOKEN
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" --value $OTEL_EXPORTER_OTLP_HEADERS
```

### Create Task and Exection Roles for Task Defintion

#### Create ExecutionRole

In the aws directory create a json file `/policies/service-execution-role.json` and add the following content

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": ["sts:AssumeRole"],
      "Effect": "Allow",
      "Principal": {
        "Service": ["ecs-tasks.amazonaws.com"]
      }
    }
  ]
}
```

Create the `CruddurServiceExecutionRole`

```sh
aws iam create-role --role-name CruddurServiceExecutionRole --assume-role-policy-document file://aws/policies/service-execution-role.json
```

Now create another json file `/policies/service-execution-policy.json` and add the following content

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter", 
        "ssm:GetParameters"
    ],
      "Resource": "arn:aws:ssm:us-east-1:183066416469:parameter/cruddur/backend-flask/*"
    }
  ]
}
```

Attach the `CruddurServiceExecutionPolicy` policy

```sh
aws iam put-role-policy --policy-name CruddurServiceExecutionPolicy --role-name CruddurServiceExecutionRole --policy-document file://aws/policies/service-execution-policy.json
```

#### Create TaskRole

Create the `CruddurTaskRole`

```sh
aws iam create-role \
    --role-name CruddurTaskRole \
    --assume-role-policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[\"sts:AssumeRole\"],
    \"Effect\":\"Allow\",
    \"Principal\":{
      \"Service\":[\"ecs-tasks.amazonaws.com\"]
    }
  }]
}"
```

Attach the `SSMAccessPolicy` policy

```sh
aws iam put-role-policy \
  --policy-name SSMAccessPolicy \
  --role-name CruddurTaskRole \
  --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[
      \"ssmmessages:CreateControlChannel\",
      \"ssmmessages:CreateDataChannel\",
      \"ssmmessages:OpenControlChannel\",
      \"ssmmessages:OpenDataChannel\"
    ],
    \"Effect\":\"Allow\",
    \"Resource\":\"*\"
  }]
}
"
```

Attach the following policies for access to `CloudWatch` and `X-Ray`

`CloudWatchFullAccess` policy

```sh
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess --role-name CruddurTaskRole
```

`AWSXRayDaemonWriteAccess` policy

```sh
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess --role-name CruddurTaskRole
```

### Create Task Definitions

Create a new folder called `aws/task-defintions` and place the following file in there:

`backend-flask.json`

```json
{
  "family": "backend-flask",
  "executionRoleArn": "arn:aws:iam::AWS_ACCOUNT_ID:role/CruddurServiceExecutionRole",
  "taskRoleArn": "arn:aws:iam::AWS_ACCOUNT_ID:role/CruddurTaskRole",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "backend-flask",
      "image": "BACKEND_FLASK_IMAGE_URL",
      "cpu": 256,
      "memory": 512,
      "essential": true,
      "portMappings": [
        {
          "name": "backend-flask",
          "containerPort": 4567,
          "protocol": "tcp", 
          "appProtocol": "http"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
            "awslogs-group": "cruddur",
            "awslogs-region": "ca-central-1",
            "awslogs-stream-prefix": "backend-flask"
        }
      },
      "environment": [
        {"name": "OTEL_SERVICE_NAME", "value": "backend-flask"},
        {"name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": "https://api.honeycomb.io"},
        {"name": "AWS_COGNITO_USER_POOL_ID", "value": ""},
        {"name": "AWS_COGNITO_USER_POOL_CLIENT_ID", "value": ""},
        {"name": "FRONTEND_URL", "value": ""},
        {"name": "BACKEND_URL", "value": ""},
        {"name": "AWS_DEFAULT_REGION", "value": ""}
      ],
      "secrets": [
        {"name": "AWS_ACCESS_KEY_ID"    , "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/AWS_ACCESS_KEY_ID"},
        {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY"},
        {"name": "CONNECTION_URL"       , "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/CONNECTION_URL" },
        {"name": "ROLLBAR_ACCESS_TOKEN" , "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" },
        {"name": "OTEL_EXPORTER_OTLP_HEADERS" , "valueFrom": "arn:aws:ssm:AWS_REGION:AWS_ACCOUNT_ID:parameter/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" }
        
      ]
    }
  ]
}
```

### Register Task Defintion

Register the task definition for the backend

```sh
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json
```

### Create Security Group

Export `VPC` id for the `VPC` name tag `cruddur-vpc`

```sh
export CRUDDUR_VPC_ID=$(aws ec2 describe-vpcs \
--filters "Name=tag:Name, Values=cruddur-vpc" \
--query "Vpcs[].VpcId" \
--output text)
echo $CRUDDUR_VPC_ID
```

<!-- Grab the `Subnet` ids

```sh
export CRUDDUR_SUBNET_ID=$(aws ec2 describe-subnets  \
--filters "Name=vpc-id, Values=$CRUDDUR_VPC_ID" \
--query 'Subnets[*].SubnetId' \
--output json | jq -r 'join(",")')
echo $CRUDDUR_SUBNET_ID
``` -->

Create security group

```sh
export CRUD_SERVICE_SG=$(aws ec2 create-security-group \
  --group-name "crud-srv-sg" \
  --description "Security group for Cruddur services on ECS" \
  --vpc-id $CRUDDUR_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_SERVICE_SG
```

Describe security group (if it already exists)

```sh
export CRUD_SERVICE_SG=$(aws ec2 describe-security-groups \
  --filters "Name=vpc-id, Values=$CRUDDUR_VPC_ID" \
  --query "SecurityGroups[*].{ID:GroupId}" \
  --output text)
echo $CRUD_SERVICE_SG
```

Add ingress rule

```sh
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 4567 \
  --cidr 0.0.0.0/0
```

### Extras
<!-- This has been done earlier 👆🏾  -->
<!-- Fix docker push error (denied: Your authorization token has expired. Reauthenticate and try again.)

```sh
aws ecr get-login-password \
    --region <region> \
| docker login \
    --username AWS \
    --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
``` -->

### Not able to use Sessions Manager to get into cluster EC2 sintance

The instance can hang up for various reasons. 
You need to reboot and it will force a restart after 5 minutes. 
So you will have to wait 5 minutes or after a timeout.

You have to use the AWS CLI. 
You can't use the `AWS Console`, it will not work as expected.

The console will only do a graceful shutdodwn. 
The CLI will do a forceful shutdown after a period of time if graceful shutdown fails.

```sh
aws ec2 reboot-instances --instance-ids i-0d15aef0618733b6d
```

### Connection via Sessions Manaager (Fargate)

[Install the Session Manager plugin on Debian](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-debian)

Install for Ubuntu

```sh
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
```

Run the install command

```sh
sudo dpkg -i session-manager-plugin.deb
```

Verify that the installation was successful

```sh
session-manager-plugin
```

### Create Services

While in the `project` directory

```sh
aws ecs create-service --cli-input-json file://aws/services/service-backend-flask.json
```

<!-- ```sh
aws ecs create-service --cli-input-json file://aws/services/service-frontend-react-js.json
``` -->

### Connect to the container

```sh
aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task dceb2ebdc11c49caadd64e6521c6b0c7 \
--container backend-flask \
--command "/bin/sh" \
--interactive
```

### Connect to the container (script)

In the backend directory, create a new script `bin/ecs/connect-to-ecs` so we can easily login to our ecs container.

```sh
# Script compatible with both zsh and bash shells
#!/usr/bin/env bash
set -e # stop if it fails at any point

if [ -z "$1" ]; then
  echo "No TASK_ID argument was supplied eg .bin/ecs/connect-to-ecs b0f2a4f926b545b9b99992b0eefc5860 backend-flask"
  exit 1
fi
TASK_ID=$1

if [ -z "$2" ]; then
  echo "No CONTAINER_NAME argument was supplied eg .bin/ecs/connect-to-ecs b0f2a4f926b545b9b99992b0eefc5860 backend-flask"
  exit 1
fi
CONTAINER_NAME=$2

aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task $TASK_ID \
--container $CONTAINER_NAME \
--command "/bin/sh" \
--interactive
```

We will make it executable:

```bash
chmod 744 bin/ecs/connect-to-ecs
```

To execute the script:

```bash
./bin/ecs/connect-to-ecs
```

<!-- ```sh
docker run -rm \
-p 4567:4567 \
-e AWS_ENDPOINT_URL="http://dynamodb-local:8000" \
-e CONNECTION_URL="postgresql://postgres:password@db:5432/cruddur" \
-e FRONTEND_URL="https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}" \
-e BACKEND_URL="https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}" \
-e OTEL_SERVICE_NAME='backend-flask' \
-e OTEL_EXPORTER_OTLP_ENDPOINT="https://api.honeycomb.io" \
-e OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=${HONEYCOMB_API_KEY}" \
-e AWS_XRAY_URL="*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*" \
-e AWS_XRAY_DAEMON_ADDRESS="xray-daemon:2000" \
-e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
-e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
-e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
-e ROLLBAR_ACCESS_TOKEN="${ROLLBAR_ACCESS_TOKEN}" \
-e AWS_COGNITO_USER_POOL_ID="${AWS_COGNITO_USER_POOL_ID}" \
-e AWS_COGNITO_USER_POOL_CLIENT_ID="5b6ro31g97urk767adrbrdj1g5" \   
-it backend-flask-prod
``` -->

# Connecting via a load balancer

### Create Security Group

Export `VPC` id for the `VPC` name tag `cruddur-vpc`

```sh
export CRUDDUR_VPC_ID=$(aws ec2 describe-vpcs \
--filters "Name=tag:Name, Values=cruddur-vpc" \
--query "Vpcs[].VpcId" \
--output text)
echo $CRUDDUR_VPC_ID
```

<!-- Grab the `Subnet` ids

```sh
export CRUDDUR_SUBNET_ID=$(aws ec2 describe-subnets  \
--filters "Name=vpc-id, Values=$CRUDDUR_VPC_ID" \
--query 'Subnets[*].SubnetId' \
--output json | jq -r 'join(",")')
echo $CRUDDUR_SUBNET_ID
``` -->

Create security group for the ALB

```sh
export CRUD_ALB_SG=$(aws ec2 create-security-group \
  --group-name "crud-alb-sg" \
  --description "Security group for Cruddur ALB on ECS" \
  --vpc-id $CRUDDUR_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_ALB_SG
```

Describe security group (if it already exists)

<!-- ```sh
export CRUD_ALB_SG=$(aws ec2 describe-security-groups \
  --filters "Name=vpc-id, Values=$CRUDDUR_VPC_ID" \
  --query "SecurityGroups[*].{ID:GroupId}" \
  --output text)
echo $CRUD_ALB_SG
``` -->

```sh
aws ec2 authorize-security-group-ingress --group-id $CRUD_ALB_SG --ip-permissions IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges="[{CidrIp=0.0.0.0/0,Description=allow http access}]" IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges="[{CidrIp=0.0.0.0/0,Description=allow secure access}]"
```

Revoke previous ingress rule for the `crud-srv-sg`

```sh
aws ec2 revoke-security-group-ingress \
    --group-name $CRUD_SERVICE_SG
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0
```

Update ingress rule for the `crud-srv-sg`

```sh
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --description "access from crudder ALB" \
  --protocol tcp \
  --port 4567 \
  --source-group $CRUD_ALB_SG
```

```sh
aws ec2 authorize-security-group-ingress --group-id sg-02d2be48c871d2a8d --ip-permissions IpProtocol=tcp,FromPort=4567,ToPort=4567,IpRanges="[{CidrIp=$CRUD_ALB_SG,Description=access from crudder ALB}]"
```

```sh
aws ec2 authorize-security-group-ingress --group-id sg-02d2be48c871d2a8d --ip-permissions IpProtocol=tcp,FromPort=4567,ToPort=4567,IpRanges="[{CidrIp=sg-0fa52a29d6d0199db,Description=access from crudder ALB}]"
```