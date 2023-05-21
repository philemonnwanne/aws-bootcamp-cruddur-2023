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
chmod 744 bin/db/test
```

To execute the script:

```bash
./bin/db/test
```
