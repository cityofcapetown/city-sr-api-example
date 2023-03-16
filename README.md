# CCT CUSTOMER SERVICE REQUESTS
This repo documents the City of Cape Town's eService API, with a particular focus on the Service Request functionality.

The main contribution is [the API Spec](./fcsa_service_request-1.0.0-resolved.json), which conforms to [the Official 
OpenAPI Spec](https://swagger.io/specification/).

## Getting Started
The main value of this API spec is using it to generate client libraries in the language of your choice!

And, what is even better, is that since OpenAPI is an open standard, there are multiple generator libraries available.

### Generating a Python client using Dockerised OpenAPI Generator Example
The below command uses the [OpenAPI Generator](https://github.com/OpenAPITools/openapi-generator) running inside a 
Docker container:

```bash
docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
                -i /local/fcsa_service_request-1.0.0-resolved.json \
                -g python \
                --additional-properties=packageName="coct_sr_api_client" \
                -o /local/dist/python
```

After running the above, you'll find a working Python client library, `coct_sr_api_client`, in `dist/python`.

You'll need to get a few dependencies: `pip3 install -r dist/python/requirements.txt`

There is a [test script](./bin/coct-get-sr-status.py) that uses this client to query the status of a SR:

To use it from this repository's root:
```bash
PYTHONPATH=./dist/python python3 ./bin/coct-get-sr-status.py -r <redacted> \
                                                             -p <redacted> \
                                                             -k <redacted> \
                                                             -v
```

And you should get a result looking like:
```
2023-03-17 00:40:54,458 __main__.<module> DEBUG: Received arguments: args.reference_number='<redacted>', args.public_key='<redacted>', args.private_key="********************************"
2023-03-17 00:40:54,458 __main__.<module> INFO: Logging into API
2023-03-17 00:40:55,179 __main__.<module> INFO: Logged into API
2023-03-17 00:40:55,179 __main__.<module> INFO: Starting an API session
2023-03-17 00:40:55,994 __main__.<module> INFO: sr_status=
{'created_on': '25.02.2023 23:08:02',
 'date_created': '25.02.2023',
 'description': 'Blocked/Overflow',
 'house': '',
 'message': '',
 'reference_number': '<redacted>',
 'status': 'In Progress',
 'street1': '',
 'subtype': '',
 'suburb1': '',
 'time_created': '23:08:02',
 'type': ''}
2023-03-17 00:40:55,994 __main__.<module> INFO: Ending API session
```
