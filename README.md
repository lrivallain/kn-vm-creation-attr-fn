# kn-echo
Simple Python function with `Flask` REST API running in Knative to echo
[CloudEvents](https://github.com/cloudevents/sdk-python).
In addition [Buildpacks](https://buildpacks.io) are used to create the
artifacts.

> **Note:** CloudEvents using structured or binary mode are supported.

Valid events will be printed out JSON-encoded, separated by their CloudEvent
`attributes` and `data` for better readability.

> **Note:** If the cloud event payload ("data") is not in JSON format, the
> (binary) payload will be represented as a string.

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

# or using a fake event
curl -i -d@testevent.json localhost:8080

HTTP/1.1 100 Continue

HTTP/1.0 204 NO CONTENT
Content-Type: application/json
Server: Werkzeug/1.0.1 Python/3.8.6
Date: Wed, 17 Feb 2021 09:16:09 GMT

# you should see the following lines printed in the docker container
* Serving Flask app "handler.py" (lazy loading)
* Environment: development
* Debug mode: on
* Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 108-388-552
2021-02-17 09:16:05,195 INFO handler Thread-3 : "***cloud event*** {"attributes": {"specversion": "1.0", "id": "08179137-b8e0-4973-b05f-8f212bf5003b", "source": "https://10.0.0.1:443/sdk", "type": "com.vmware.event.router/event", "datacontenttype": "application/json", "subject": "VmPoweredOffEvent", "time": "2020-02-11T21:29:54.9052539Z"}, "data": {"Key": 9902, "ChainId": 9895, "CreatedTime": "2020-02-11T21:28:23.677595Z", "UserName": "VSPHERE.LOCAL\\Administrator", "Datacenter": {"Name": "testDC", "Datacenter": {"Type": "Datacenter", "Value": "datacenter-2"}}, "ComputeResource": {"Name": "cls", "ComputeResource": {"Type": "ClusterComputeResource", "Value": "domain-c7"}}, "Host": {"Name": "10.185.22.74", "Host": {"Type": "HostSystem", "Value": "host-21"}}, "Vm": {"Name": "test-01", "Vm": {"Type": "VirtualMachine", "Value": "vm-56"}}, "Ds": null, "Net": null, "Dvs": null, "FullFormattedMessage": "test-01 on  10.0.0.1 in testDC is powered off", "ChangeTag": "", "Template": false}}
```