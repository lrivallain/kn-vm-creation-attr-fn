# kn-echo
Simple Python function with `Flask` REST API running in Knative to echo
[CloudEvents](https://github.com/cloudevents/sdk-python).
In addition [Buildpacks](https://buildpacks.io) are used to create the
artifacts.

> **Note:** CloudEvents using structured or binary mode are supported.

# Deployment (Knative)

**Note:** The following steps assume a working Knative environment using the
`default` broker. The Knative `service` and `trigger` will be installed in the
`default` Kubernetes namespace, assuming that the broker is also available there.

```bash
# create the service
kn service create kn-echo --port 8080 --image embano1/kn-echo:latest

# create the trigger
kn trigger create kn-echo --broker default --sink ksvc:kn-echo
```

# Build with `pack`

- Requirements:
  - `pack` (see: https://buildpacks.io/docs/app-developer-guide/)
  - Docker

```bash
IMAGE=embano1/kn-echo:latest
pack build -B gcr.io/buildpacks/builder:v1 ${IMAGE}
```

## Verify the image works by executing it locally:

```bash
docker run -e PORT=8080 -it --rm -p 8080:8080 embano1/kn-echo:latest

# now in a separate window or use -d in the docker cmd above to detach
curl -i localhost:8080
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 62
Server: Werkzeug/1.0.1 Python/3.8.6
Date: Mon, 16 Nov 2020 11:54:43 GMT

{
  "message": "POST to this endpoint to echo cloud events"
}
```