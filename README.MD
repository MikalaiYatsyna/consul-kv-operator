# Kubernetes CRD to populate consul KV

## Quick Start

### Build image

### Inputs

| Name                | Description          | Required | Default             |
|---------------------|----------------------|----------|---------------------|
| `python_image`      | Base python image    | no       | "python:slim"      |
| `image_name`        | Image name           | no       | "consul-kv-operator" |
| `image_tag`         | Docker tag for image | yes      | -                   |


```bash
packer build -var image_tag=<tag> .
```

### Deploy Helm chart

```bash
helm install consul-kv-crd ./helm --set image.tag=<tag>
```

### Check resource
```bash
kubectl get crd
kubectl get pods
```

## **Usage**
Create and apply yaml with content
```yaml
apiVersion: extensions.logistic.com/v1
kind: ConsulKv
metadata:
    name: user-service-config
    labels:
      app: user-service
spec:
  host: consul-server
  path: {{.Release.Namespace}}/config/{{.Chart.Name}}/data
  valueType: ["KV", "YAML", "PROPERTIES"] # one of values
  value:
    spring:
        application:
            name: user-service
```
