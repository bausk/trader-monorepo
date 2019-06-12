import json
import os
import sys
import importlib
import glob
import re


rootpath = os.path.join(os.path.dirname(__file__), os.pardir)


def get_variables(*envs):
    special_vars = {
    }
    common_vars = {}
    for env in envs:
        env_config_files = glob.glob('{}/.secrets/[!_]*.{}.json'.format(rootpath, env))
        env_common_files = glob.glob('{}/.secrets/_*.{}.json'.format(rootpath, env))
        for config_file_name in env_config_files:
            try:
                service = re.search(
                    '(\w+)\.{}\.json'.format(env),
                    config_file_name
                ).group(1)
                if service not in special_vars:
                    special_vars[service] = {}
                with open(config_file_name, 'r') as varfile:
                    json_string = varfile.read()
                    json_variables = json.loads(json_string)
                    for entry in json_variables:
                        key = entry.get('key', None)
                        value = entry.get('value', '')
                        if key:
                            if type(value) is str:
                                special_vars[service][key] = value
                            if type(value) is dict:
                                executor_name = value['script']
                                executor = importlib.import_module('custom.{}'.format(executor_name))
                                special_vars[service][key] = executor.script()
            except Exception:
                pass
        for common_file_name in env_common_files:
            try:
                with open(common_file_name, 'r') as varfile:
                    json_string = varfile.read()
                    json_variables = json.loads(json_string)
                    for entry in json_variables:
                        key = entry.get('key', None)
                        value = entry.get('value', '')
                        if key:
                            if type(value) is str:
                                common_vars[key] = value
                            if type(value) is dict:
                                executor_name = value['script']
                                executor = importlib.import_module('custom.{}'.format(executor_name))
                                common_vars[key] = executor.script()
            except Exception:
                pass
    return common_vars, special_vars