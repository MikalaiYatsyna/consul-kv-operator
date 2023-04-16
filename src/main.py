import os

import consulate
import kopf
import yaml

NAME = os.getenv('NAME')
GROUP = os.getenv('GROUP')
version = os.getenv('VERSION')


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


@kopf.on.create(group=GROUP, version=version, singular=NAME, )
@kopf.on.update(group=GROUP, version=version, singular=NAME)
def on_create(spec, **kwargs):
    consul = consulate.Consul(host=f"{spec.get('host')}")
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


@kopf.on.delete(group=GROUP, version=version, singular=NAME)
def on_delete(spec, **kwargs):
    consul = consulate.Consul(host=f"{spec.get('host')}")
    consul.kv.delete(f"{spec.get('path')}", recurse=True)
