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

