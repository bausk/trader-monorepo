import json
import os
import sys
from getvars import get_variables


rootpath = os.path.join(os.path.dirname(__file__), os.pardir)

if __name__ == '__main__':
    common, special = get_variables('production')
    for service, variables in special.items():
        final_varset = {**common, **variables}
        print('> Provisioning secrets for service {}...\n'.format(service))
        with open('{}/{}/secrets.json'.format(rootpath, service), 'w') as secrets:
            json.dump(final_varset, secrets, sort_keys=True, indent=2)
