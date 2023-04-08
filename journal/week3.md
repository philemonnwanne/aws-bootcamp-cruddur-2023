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

```bash
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

## Conditionally show components based on logged in or logged out

Add the following to`HomeFeedPage.js` file

```js
import { Auth } from 'aws-amplify';

// set a state
const [user, setUser] = React.useState(null);

// check if we are authenicated
const checkAuth = async () => {
  Auth.currentAuthenticatedUser({
    // Optional, By default is false.
    // If set to true, this call will send a 
    // request to Cognito to get the latest user data
    bypassCache: false 
  })
  .then((user) => {
    console.log('user',user);
    return Auth.currentAuthenticatedUser()
  }).then((cognito_user) => {
      setUser({
        display_name: cognito_user.attributes.name,
        handle: cognito_user.attributes.preferred_username
      })
  })
  .catch((err) => console.log(err));
};

// check when the page loads if we are authenicated
React.useEffect(()=>{
  loadData();
  checkAuth();
}, [])
```

We will update `ProfileInfo.js`

```js
import { Auth } from 'aws-amplify';

const signOut = async () => {
  try {
      await Auth.signOut({ global: true });
      window.location.href = "/"
  } catch (error) {
      console.log('error signing out: ', error);
  }
}
```

Next we will update the signin page

```js
import { Auth } from 'aws-amplify';

const onsubmit = async (event) => {
    setErrors('')
    event.preventDefault();
      Auth.signIn(email, password)
        .then(user => {
          localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
          window.location.href = "/"
        })
        .catch(error => {
          if (error.code == 'UserNotConfirmedException') {
            window.location.href = "/confirm"
          }
          setErrors(error.message)
        });
    return false
}
```

### SignUp Page

```js
import { Auth } from 'aws-amplify';

  const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    try {
      const { user } = await Auth.signUp({
        username: email,
        password: password,
        attributes: {
          name: name,
          email: email,
          preferred_username: username,
        },
        autoSignIn: { // optional - enables auto sign in after user is confirmed
          enabled: true,
        }
      });
      console.log(user);
      window.location.href = `/confirm?email=${email}`
    } catch (error) {
      console.log(error);
      setErrors(error.message)
    }
    return false
  }
```

### Confirmation Page

```js
import { Auth } from 'aws-amplify';

const resend_code = async (event) => {
    setErrors('')
    try {
      await Auth.resendSignUp(email);
      console.log('code resent successfully');
      setCodeSent(true)
    } catch (err) {
      // does not return a code
      // does cognito always return english
      // for this to be an okay match?
      console.log(err)
      if (err.message == 'Username cannot be empty'){
        setErrors("You need to provide an email in order to send Resend Activiation Code")   
      } else if (err.message == "Username/client id combination not found."){
        setErrors("Email is invalid or cannot be found.")   
      }
    }
  }

  const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    try {
      await Auth.confirmSignUp(email, code);
      window.location.href = "/"
    } catch (error) {
      setErrors(error.message)
    }
    return false
  }
  ```

  ## Recovery Page

  ```js
import { Auth } from 'aws-amplify';

const onsubmit_send_code = async (event) => {
    event.preventDefault();
    setErrors('')
    Auth.forgotPassword(username)
    .then((data) => setFormState('confirm_code') )
    .catch((err) => setErrors(err.message) );
    return false
  }
  
  const onsubmit_confirm_code = async (event) => {
    event.preventDefault();
    setErrors('')
    if (password == passwordAgain){
      Auth.forgotPasswordSubmit(username, code, password)
      .then((data) => setFormState('success'))
      .catch((err) => setErrors(err.message) );
    } else {
      setErrors('Passwords do not match')
    }
    return false
  }
  ```

## Authenticating Server Side

Add in the `HomeFeedPage.js` a header to pass along the access token

```js
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
  }
```

Add to the app.py

```python
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)
```

## Setup up Cognito Authentication

Add to the `requirements.txt`

```txt
...
Flask_AWSCognito
```

While in the backend directory run

```bash
pip install -r requirements.txt
```

Append the following to the `backend service`in the compose file

```yaml
AWS_COGNITO_USER_POOL_ID: ""
AWS_COGNITO_USER_POOL_CLIENT_ID: ""
```

`Note:` Restart your compose file for these changes to take effect

Move to the backend directory and create a directory `lib`

```bash
mkdir lib
```

Now create a python file `cognito_jwt_token.py`

```bash
touch cognito_jwt_token.py
```

Add the following lines of code to `cognito_jwt_token.py`

```python
HTTP_HEADER = "Authorization"

import time
import requests
from jose import jwk, jwt
from jose.exceptions import JOSEError
from jose.utils import base64url_decode


class FlaskAWSCognitoError(Exception):
  pass

class TokenVerifyError(Exception):
  pass

def extract_access_token(request_headers):
  access_token = None
  auth_header = request_headers.get(HTTP_HEADER)
  if auth_header and " " in auth_header:
    _, access_token = auth_header.split()
  return access_token
    
class CognitoJwtToken:
  def __init__(self, user_pool_id, user_pool_client_id, region, request_client=None):
    self.region = region
    if not self.region:
        raise FlaskAWSCognitoError("No AWS region provided")
    self.user_pool_id = user_pool_id
    self.user_pool_client_id = user_pool_client_id
    self.claims = None
    if not request_client:
        self.request_client = requests.get
    else:
        self.request_client = request_client
    self._load_jwk_keys()

  def _load_jwk_keys(self):
    keys_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
    try:
      response = self.request_client(keys_url)
      self.jwk_keys = response.json()["keys"]
    except requests.exceptions.RequestException as e:
      raise FlaskAWSCognitoError(str(e)) from e

  @staticmethod
  def _extract_headers(token):
    try:
      headers = jwt.get_unverified_headers(token)
      return headers
    except JOSEError as e:
      raise TokenVerifyError(str(e)) from e

  def _find_pkey(self, headers):
    kid = headers["kid"]
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(self.jwk_keys)):
      if kid == self.jwk_keys[i]["kid"]:
        key_index = i
        break
    if key_index == -1:
      raise TokenVerifyError("Public key not found in jwks.json")
    return self.jwk_keys[key_index]

  @staticmethod
  def _verify_signature(token, pkey_data):
    try:
      # construct the public key
      public_key = jwk.construct(pkey_data)
    except JOSEError as e:
      raise TokenVerifyError(str(e)) from e
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit(".", 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
      raise TokenVerifyError("Signature verification failed")

  @staticmethod
  def _extract_claims(token):
    try:
      claims = jwt.get_unverified_claims(token)
      return claims
    except JOSEError as e:
      raise TokenVerifyError(str(e)) from e

  @staticmethod
  def _check_expiration(claims, current_time):
    if not current_time:
      current_time = time.time()
    if current_time > claims["exp"]:
      raise TokenVerifyError("Token is expired")  # probably another exception

  def _check_audience(self, claims):
    # and the Audience  (use claims['client_id'] if verifying an access token)
    audience = claims["aud"] if "aud" in claims else claims["client_id"]
    if audience != self.user_pool_client_id:
      raise TokenVerifyError("Token was not issued for this audience")

  def verify(self, token, current_time=None):
    """ https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py """
    if not token:
      raise TokenVerifyError("No token provided")

    headers = self._extract_headers(token)
    pkey_data = self._find_pkey(headers)
    self._verify_signature(token, pkey_data)

    claims = self._extract_claims(token)
    self._check_expiration(claims, current_time)
    self._check_audience(claims)

    self.claims = claims
    return claims
```

Now add the following to `app.py`

```python
from lib.cognito_jwt_token import CognitoJwtToken, TokenVerifyError, extract_access_token

# Everything here goes under the Flask app initiation 
cognito_jwt_token = CognitoJwtToken(
  user_pool_id = os.getenv("AWS_COGNITO_USER_POOL_ID"), 
  user_pool_client_id = os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"),
  region = os.getenv("AWS_DEFAULT_REGION")
)
```

Modify the route `/api/activities/home` in `app.py`
```python
@app.route("/api/activities/home", methods=['GET'])
def data_home():
  access_token = extract_access_token (request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    # authenticated request
    app.logger.debug('authenticated')
    app.logger.debug(claims)
  except TokenVerifyError as e:
    # unauthenticated request
    app.logger.debug(e)
    app.logger.debug("unauthenicated")
    data = HomeActivities.run()
  return data, 200
```

