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