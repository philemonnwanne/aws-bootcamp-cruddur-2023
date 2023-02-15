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

## Setting Up the AWS CLI

### Install AWS CLI

- We are going to install the AWS CLI when our Gitpod enviroment lanuches.
- We are going to set AWS CLI to use `partial autoprompt` mode which makes it easier to debug CLI commands.
- The bash commands we are using can be found here [AWS CLI Install Instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

Update the `.gitpod.yml` file in the projects root directory to include the following task.

```bash
tasks:
  - name: aws-cli
    env:
      AWS_CLI_AUTO_PROMPT: on-partial
    init: |
      # move one directory backwords and create a new directory called `interim`
      cd /workspace && mkdir interim
      # get the AWS CLI zip file
      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /workspace/interim/"awscliv2.zip"
      # decompress the aws zip file
      unzip awscliv2.zip
      # install the aws package
      sudo ./aws/install
      # switch to the projects main directory
      cd $THEIA_WORKSPACE_ROOT
      # cleanup to avoid unnecessary clutter
      rm -rf ../interim
```

