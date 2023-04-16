# Kubernetes Operator to populate Consul KV storage

## Quick Start
Used to update Consul KV in Kubernetes-native GitOps way

### Inputs
| Name           | Description          | Required | Default              |
|----------------|----------------------|----------|----------------------|
| `python_image` | Base python image    | no       | "python:slim"        |
| `image_name`   | Image name           | no       | "consul-kv-operator" |
| `image_tag`    | Docker tag for image | yes      | -                    |

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
apiVersion: extensions.logisticsonline.uk
kind: ConsulKV
metadata:
    name: user-service-config
    labels:
      app: user-service
spec:
  host: consul-server
  path: {{.Release.Namespace}}/config/{{.Chart.Name}}/data
  valueType: ["KV", "YAML", "PROPERTIES"]
  value:
    spring:
        application:
            name: user-service
```
