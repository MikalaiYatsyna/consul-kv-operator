import consulate
import kopf
import kubernetes.client as k8s_client
import kubernetes.config as k8s_config
import yaml
from kubernetes.client import ApiException

group = "extensions.logistic.com"
name = "ckvs"
version = 'v1'
meta_name = ".".join([name, group])

consul_kv_crd = k8s_client.V1CustomResourceDefinition(
    api_version="apiextensions.k8s.io/v1",
    kind="CustomResourceDefinition",
    metadata=k8s_client.V1ObjectMeta(name=meta_name),
    spec=k8s_client.V1CustomResourceDefinitionSpec(
        group=group,
        versions=[k8s_client.V1CustomResourceDefinitionVersion(
            name="v1",
            served=True,
            storage=True,
            schema=k8s_client.V1CustomResourceValidation(
                open_apiv3_schema=k8s_client.V1JSONSchemaProps(
                    type="object",
                    properties={"spec": k8s_client.V1JSONSchemaProps(
                        type="object",
                        properties={
                            "valueType": k8s_client.V1JSONSchemaProps(type="string", enum=["YAML", "PROPERTIES", "KV"]),
                            "value": k8s_client.V1JSONSchemaProps(type="object",
                                                                  x_kubernetes_preserve_unknown_fields=True),
                            "host": k8s_client.V1JSONSchemaProps(type="string"),
                            "path": k8s_client.V1JSONSchemaProps(type="string"),
                        }
                    )}
                ),
            )
        )],
        scope="Cluster",
        names=k8s_client.V1CustomResourceDefinitionNames(
            plural=name,
            singular="ckv",
            kind="ConsulKv",
            short_names=["ckv"]
        )
    )
)

try:
    k8s_config.load_kube_config()
except k8s_config.ConfigException:
    k8s_config.load_incluster_config()


def create_crd(crd):
    try:
        api_instance.create_custom_resource_definition(crd)
    except ApiException as e:
        if e.status == 409:
            api_instance.patch_custom_resource_definition(meta_name, crd)
        else:
            raise e


with k8s_client.ApiClient() as api_client:
    api_instance = k8s_client.ApiextensionsV1Api(api_client)
    create_crd(consul_kv_crd)


def dict_to_pair(data, path="", result=None):
    if not path.endswith('/'):
        path = f"{path}/"
    if result is None:
        result = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                result.append(f"{path}{k}={v}")
            elif isinstance(v, object):
                dict_to_pair(v, f"{path}{k}", result)
    elif isinstance(data, str):
        result.append(f"{path}={data}")
    return result


@kopf.on.create(group=group, version=version, plural=name)
@kopf.on.update(group=group, version=version, plural=name)
def on_create(spec, **kwargs):
    consul = consulate.Consul(host=f"{spec['host']}")
    value_type = spec['valueType']
    path = spec['path']
    value = spec['value']

    if value_type == 'YAML' or value_type == 'PROPERTIES':
        consul.kv.set(f"{path}/data", yaml.safe_dump(value))
    elif value_type == 'KV':
        result = []
        for item in dict_to_pair(value, f"{path}", result):
            (k, v) = item.split("=")
            consul.kv.delete(k, recurse=True)
            # TODO fix update with replace
            consul.kv.set(k, v)


@kopf.on.delete(group=group, version=version, plural=name)
def on_delete(spec, **kwargs):
    consul = consulate.Consul(host=f"{spec['host']}")
    path = spec['path']

    consul.kv.delete(f"{path}", recurse=True)
