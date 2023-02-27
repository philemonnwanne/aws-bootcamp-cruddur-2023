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

## Configure OpenTelemetry for Python

This guide will help you add OpenTelemetry to our backend service, and ensure that instrumentation data is being sent to Honeycomb.

## Requirements

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

## Initialize

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

## Configure and Run

Configure `OpenTelemetry` to send events to `Honeycomb` using environment variables.

`Note:` The header `x-honeycomb-team` is your `API key`. Your service name will be used as the Service Dataset in Honeycomb, which is where data is stored. The service name is specified by `OTEL_SERVICE_NAME`.

```env
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.honeycomb.io/"
export OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=your-api-key"
export OTEL_SERVICE_NAME="your-service-name"
```

## Troubleshooting API Keys
If you're not recieving any data in honeycomb it might be because you are using the wrong API keys. Try the below steps to find out if  data is actually being sent out of your app.

Edit `app.py` and add the following lines to it:

```python
...
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

...
# Simple Span Processor [show output in the logs withing the backend-flask app (STDOUT)]
simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)
```

## @Jessitrons hack for Confirming honeycomb API Keys

Visit `honecomb-whoami.glitch.me` and paste in your `HONEYCOMB_API_KEY`. This will return some info regarding the API Key