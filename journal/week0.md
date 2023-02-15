<p align=right> 
<a href="https://gitpod.io/#https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023">
  <img
    src="https://img.shields.io/badge/Contribute%20with-Gitpod-908a85?logo=gitpod"
    alt="Contribute with Gitpod"
    style="text-align: right"
  />
</a>
</p>

# Week 0 — Billing and Architecture

## Creating an IAM Admin User
### Create a new User
This section generally involves 3 steps

#### Step 1
Specify user details
- Go to (IAM Users Console](https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/home) and click on `User`
- Click on the blue `Add Users` button indicated on the top right corner
- Specify a username and tick the `Enable console access` checkbox for the user. This step is important as we plan on running commands with the user via the CLI
- Set a custom password for the user and click on the `Next` button

#### Step 2
Set permissions
- Select the `Add user to a group` option and click on the `Create group` button
- Give the group a name, in my own case called `sudo` and from the list of permission policies apply the `AdministratorAccess` to the group
- Click on `Create user group`
- Select the admin group you just created and click on the `Next` button

#### Step 3
Review and create
- Make sure that all your details are correct then click on the `Create User` button

### Generate IAM Credentials
- After creating the user, click into the user and click on the `Security credentials` section
- Scroll downwards and look for the `Access keys` section
- Click on `Create Access Key`
- Choose the `Command Line Interface (CLI)` option and click next
- Click on `Create access key`
- Download the generated CSV containing your IAM credentials

## Setting Up the AWS CLI

### Install AWS CLI

- We are going to auto install the AWS CLI when our Gitpod enviroment lanuches.
- We are going to set AWS CLI to use `partial autoprompt` mode which makes it easier to use AWS CLI commands.
- The bash commands we are using can be found here [AWS CLI Install Instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- These commands can also be run individually on the terminal to perform a manual installation.

Update the `.gitpod.yml` file in the projects root directory to include the following task.

```bash
tasks:
  - name: aws-cli
    env:
      AWS_CLI_AUTO_PROMPT: on-partial
    init: |
      # move one step upwards and create a new directory called `interim` then move into that directory
      mkdir ../interim && cd ../interim
      # get the AWS CLI zip file
      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
      # decompress the aws zip file
      unzip awscliv2.zip
      # install the aws package
      sudo ./aws/install
      # switch to the projects main directory
      cd $THEIA_WORKSPACE_ROOT
      # cleanup to avoid unnecessary clutter
      rm -rf ../interim
```

### Set AWS Env Vars

We will set these credentials for the current bash terminal
```php
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_DEFAULT_REGION=""
```

Run the below commands to make Gitpod persist the credentials after a workspace relaunch
```php
gp env AWS_ACCESS_KEY_ID=""
gp env AWS_SECRET_ACCESS_KEY=""
gp env AWS_DEFAULT_REGION=us-east-1
```

### Confirm your Identity

Run the following command to ensure that the AWS CLI is working and you are the expected user
```bash
aws sts get-caller-identity
```

You should see something like this:
```json
{
    "UserId": "DGT5ZRJKDT2ONP4ET7YE8",
    "Account": "5567-0000-34211",
    "Arn": "arn:aws:iam::556700034211:user/phil"
}
```
Don't bother copying the following fake details 💀


## Enable Billing 

We need to turn on Billing Alerts to recieve alerts...

- In your Root Account go to the [Billing Page](https://console.aws.amazon.com/billing/)
- Under `Billing Preferences` Choose `Receive Billing Alerts`
- Save Preferences


## Creating a Billing Alarm

### Create a SNS Topic

- We need an SNS topic before we create an alarm.
- The job of an SNS topic is to send us an alert when we get overbilled
- [aws sns create-topic](https://docs.aws.amazon.com/cli/latest/reference/sns/create-topic.html)

We'll create a SNS Topic called `billing-alarm`
```bash
aws sns create-topic --name billing-alarm
```
Which will return a TopicARN. It's important to note that this action is idempotent, so if the requester already owns a topic with the specified name, that topic’s ARN is returned without creating a new topic.

You can confirm that your topic was created by running the following command
```bash
aws sns list-topics
```

you should get an output like below
```json
{
    "Topics": [
        {
            "TopicArn": "arn:aws:sns:us-east-1:183066416469:billing-alarm"
        }
    ]
}
```

We will now create a subscription then supply the `TopicARN` and our `Email`. The following subscribe command subscribes an email address to the topicARN created earlier.
```sh
aws sns subscribe \
    --topic-arn TopicARN \
    --protocol email \
    --notification-endpoint "your email goes in here"
```
You should get an output below and also an email a few seconds later
```json
{
    "SubscriptionArn": "pending confirmation"
}
```

Check your email and confirm the subscription, which should redirect you to your browser and display the following page
![SNS-sub-confirmation](https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023/blob/main/journal/images/week0/sns-sub-confirm.png)

#### Create an Alarm

- [aws cloudwatch put-metric-alarm](https://docs.aws.amazon.com/cli/latest/reference/cloudwatch/put-metric-alarm.html)
- [Create an Alarm via AWS CLI](https://aws.amazon.com/premiumsupport/knowledge-center/cloudwatch-estimatedcharges-alarm/)
- We need to update the configuration json script with the TopicARN we generated earlier
- We will use a json file because --metrics is is required for expressions and so its easier to us a JSON file.

```bash
aws cloudwatch put-metric-alarm --cli-input-json file://aws/json/alarm_config.json
```
