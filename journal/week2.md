<p align=right> 
<a href="https://gitpod.io/#https://github.com/philemonnwanne/aws-bootcamp-cruddur-2023">
  <img
    src="https://img.shields.io/badge/Contribute%20with-Gitpod-908a85?logo=gitpod"
    alt="Contribute with Gitpod"
    style="text-align: right"
  />
</a>
</p>

# Week 2 — Distributed Tracing

## Required Homework/Tasks

## Intrument with HoneyComb

### Configure OpenTelemetry for Python

This guide will help you add OpenTelemetry to our backend service, and ensure that instrumentation data is being sent to Honeycomb.

### Requirements

These instructions will explain how to set up manual instrumentation for a service written in Python. In order to follow along, you will need:

- Python 3.6 or higher
- An `app` written in Python
- A Honeycomb `API Key`

## Adding Instrumentation

### Install Packages

Install these packages to instrument a Flask app with OpenTelemetry:

Add the following to our `requirements.txt` file

```txt
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-flask
opentelemetry-instrumentation-requests
```

### Initialize

Add these lines to your existing Flask app initialization file `app.py` (or similar). These updates will create and initialize a `tracer` and `Flask instrumentation` to send data to Honeycomb.

```python
# Initialize tracing with HoneyComb
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Initialize automatic instrumentation with Flask
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```

### Configure and Run

Configure `OpenTelemetry` to send events to `Honeycomb` using environment variables.

`Note:` The header `x-honeycomb-team` is your `API key`. Your service name will be used as the Service Dataset in Honeycomb, which is where data is stored. The service name is specified by `OTEL_SERVICE_NAME`.

```env
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.honeycomb.io/"
export OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=your-api-key"
export OTEL_SERVICE_NAME="your-service-name"
```

### Troubleshooting API Keys

If you're not recieving any data in honeycomb it might be because you are using the wrong API keys. Try the below steps to find out if data is actually being sent out of your app.

Edit `app.py` and add the following lines to it:

```python
...
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

...
# Simple Span Processor [show output in the logs withing the backend-flask app (STDOUT)]
simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)
```

### @Jessitrons hack for Confirming honeycomb API Keys

Visit `honecomb-whoami.glitch.me` and paste in your `HONEYCOMB_API_KEY`. This will return some info regarding the API Key

### Creating a Tracer

To create spans, you need to get a `Tracer`. Add the following lines of code to the `services/home_activities.py file`.

```python
from opentelemetry import trace

tracer = trace.get_tracer("tracer.name.here")
```

When you create a Tracer, OpenTelemetry requires you to give it a name as a string. This string is the only required parameter.

When traces are sent to Honeycomb, the name of the `Tracer` is turned into the `library.name` field, which can be used to show all spans created from a particular `tracer`.

The `library.name` field is also used with traces created from instrumentation libraries.

### Creating Spans

Now we have a tracer configured, we can create spans to describe what is happening in your application. For example, this could be a HTTP handler, a long running operation, or a database fetch.

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("http-handler"):
    with tracer.start_as_current_span("my-cool-function"):
        # do something
```

### Adding Attributes to Spans

It is often beneficial to add context to a currently executing span in a trace. For example, you may have an application or service that handles users and you want to associate the user with the span when querying your dataset in Honeycomb. In order to do this, get the current span from the context and set an attribute with the user ID:

```python
from opentelemetry import trace

...

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("http-handler") as outer_span:
    with tracer.start_as_current_span("my-cool-function") as inner_span:
        outer_span.set_attribute("outer", True)
        inner_span.set_attribute("inner", True)

...

span = trace.get_current_span()
span.set_attribute("user.id", user.id())
```

## Instrument with AWS X-Ray

### :mega: OpenTelemetry Python with AWS X-Ray

AWS X-Ray supports using OpenTelemetry Python and the AWS Distro for OpenTelemetry (ADOT) Collector to instrument your application and send trace data to X-Ray. The OpenTelemetry SDKs are an industry-wide standard for tracing instrumentation.

### Installing

The AWS X-Ray SDK for Python is compatible with Python 2.7, 3.4, 3.5, and 3.6.

Install the SDK using the following command (the SDK's non-testing dependencies will be installed).

```
pip install aws-xray-sdk
```

Add the SDK as a dependency in your requirements.txt file.

#### Example `requirements.txt`

```txt
aws-xray-sdk==2.4.2
boto3==1.4.4
botocore==1.5.55
Django==1.11.3
```

`Note` If you use Elastic Beanstalk to deploy your application, Elastic Beanstalk installs all of the packages in requirements.txt automatically.

Add the following to

### Tracing incoming requests with the X-Ray SDK for Python middleware

When you add the middleware to your application and configure a segment name, the X-Ray SDK for Python creates a segment for each sampled request.

The X-Ray SDK for Python supports the following middleware to instrument incoming HTTP requests:

- Django
- Flask
- Bottle

## Adding the middleware to your application (flask)

To instrument your Flask application, first configure a segment name on the xray_recorder. Then, use the XRayMiddleware function to patch your Flask application in code.

Add the following lines of code to `app.py`

```python
...
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

app = Flask(__name__)

...
xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service='cruddur-backend-flask', dynamic_naming=xray_url)
XRayMiddleware(app, xray_recorder)
```

This tells the X-Ray recorder to trace requests served by your Flask application with the default sampling rate. You can configure the recorder in code to apply custom sampling rules or change other settings.

### Create an AWS X-Ray group

```bash
FLASK_ADDRESS="https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
aws xray create-group \
   --group-name "Cruddur" \
   --filter-expression "service(\"cruddur-backend-flask\") {fault OR error}"
```

`Note` You won't be able to create a group if it already exists.

### Create a sampling rule

Move into the `backend-flask` directory and create a `xray.json` file

```json
{
  "SamplingRule": {
      "RuleName": "Cruddur",
      "ResourceARN": "*",
      "Priority": 9000,
      "FixedRate": 0.1,
      "ReservoirSize": 5,
      "ServiceName": "Cruddur",
      "ServiceType": "*",
      "Host": "*",
      "HTTPMethod": "*",
      "URLPath": "*",
      "Version": 1
  }
}
```

While still in the `backend-flask` directory run the below command to generate a `sampling rule`.

```bash
aws xray create-sampling-rule --cli-input-json file://backend-flask/xray.json
```

Add the following variables to the `backend-flask` service docker-compose file

```env
AWS_XRAY_URL: "*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*"
AWS_XRAY_DAEMON_ADDRESS: "xray-daemon:2000"
```

## CloudWatch Logs

Add the following to the `requirements.txt` file.

```txt
...
watchtower
```

Use the following configuration to send Flask logs to a CloudWatch Logs stream called `cruddur`:

Add the following lines of code to `app.py`

```python
...
import watchtower, logging
from time import strftime

# Configuring Logger to Use CloudWatch
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
LOGGER.addHandler(console_handler)
LOGGER.addHandler(cw_handler)

@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response
```

We'll log something in an API endpoint

```python
LOGGER.info('IAM Active Logger! from  /api/activities/home')
```

Set the following environment vars in the `backend-flask` service section of `docker-compose.yml`

```yml
AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
```
`Note` Passing `AWS_REGION` doesn't seem to get picked up by `boto3` so pass `AWS_DEFAULT_REGION` instead
