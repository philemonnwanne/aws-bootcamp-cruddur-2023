# Week 3 — Decentralized Authentication

## Setup Cognito
Go to the AWS console and setup an AWS Cognito userpool

## Install Amplify
While in the frontend directory, run the the following commands

```bash
npm install aws-amplify --save
```
This will add the `aws-amplify` package as a dependency in the `package.json` file

## Configure Amplify
Move into the frontend `src` directory

``bash
cd frontend/src
```

 Add the following line of code to the `App.js` file

```js
import { Amplify } from 'aws-amplify';

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    region: process.env.REACT_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```