import json
import os


def script():
    rootpath = os.path.join(os.path.dirname(__file__), os.pardir)
    with open('{}/../.secrets/googlekey.json'.format(rootpath), 'r') as credfile:
        key = credfile.read()
        serialized = json.dumps(json.loads(key))
    return serialized
