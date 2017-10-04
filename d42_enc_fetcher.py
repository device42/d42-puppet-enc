import os, sys, json, logging
import argparse
import requests
from ruamel import yaml
from ruamel.yaml import YAML

import warnings
import logging

# suppress warnings from requests for now.
# TODO: log them instead
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description="d42_enc_fetcher")

# d42 will be queried for --name.
# the puppet integration sets name of puppet nodes to the name of its ssl cert.
parser.add_argument("name", help='Name of node to return enc for.')
# parser.add_argument('-n', '--name', help='Name of node to return enc for.  Should be same as certname.')
parser.add_argument('-v', '--verbose', help='Prints more information.', action='store_true')
parser.add_argument('-c', '--config', help='set config location, otherwise', default='settings.yaml')

verbose = False

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


yaml = YAML()
yaml.default_flow_style = False


def printer(msg = None):
    global verbose
    if not verbose:
        return 0
    elif verbose == True:
        print "\n%s\n" % (msg)
        return 0

def get_config(cfgpath):
    if not os.path.exists(cfgpath):
        if not os.path.exists(os.path.join(CUR_DIR, cfgpath)):
            raise ValueError("Config file %s is not found!" % cfgpath)
        cfgpath = os.path.join(CUR_DIR, cfgpath)
    with open(cfgpath, 'r') as cfgf:
        config = yaml.load(cfgf.read())
    return config

'''
input:
    node_classes_obj: object containing node classification JSON
output:
    node_classes_obj: object with format {classes: {nodeclasses} }
this function makes sure that there is only one top level classes key
'''
def top_level_classes_reducer(node_classes_obj):
    if node_classes_obj['classes']['classes']:
        node_classes_obj = node_classes_obj['classes']
    return node_classes_obj

'''
input:
    d42_node: device object returned from d42 api
    node_classes_field: custom field on device that contains node classes
output:
    node_classes_yaml: node classes as json
'''
def process_d42_node_enc(d42_node, node_classes_field):
    yaml = YAML()
    yaml.default_flow_style = False
    printer('node_classes_field is set to: %s' % (node_classes_field))
    # printer(json.dumps(d42_node, indent=4, sort_keys=True ))
    node_classes_obj = { "classes": json.loads(node['value'])  for node in d42_node['custom_fields'] if "node_classes" in node['key'] }
    node_classes_obj = top_level_classes_reducer(node_classes_obj)
    #printer(node_classes_obj)

    # node_classes_yaml = yaml.dump(node_classes_obj, sys.stdout)

    #printer(node_classes_yaml) # this is printing NONE



    return node_classes_obj

def fetch_node_classification(d42_host, device_name, auth_user, auth_pass, node_classes_field, verify_cert=False):
    method = "GET"
    headers = {}
    url = "https://%s/api/1.0/devices/name/%s" % (d42_host, device_name)
    response = requests.request(method, url,
                                auth=(auth_user, auth_pass),
                                headers=headers, verify=verify_cert
                               )
    resp = response.json()

    node_classification = process_d42_node_enc(resp, node_classes_field)

    return node_classification

def main():
    global verbose
    # TODO handle other input args
    args = parser.parse_args()
    if args.verbose:
        verbose = True
    if args.name:
        printer('fetching node classification for: ' + args.name)

    config = get_config(args.config)

    device_name = args.name
    d42_host = config['device42']['host']

    printer('d42 appliance host:' + config['device42']['host'])

    node_classes = fetch_node_classification(
        d42_host=d42_host,
        device_name=device_name,
        auth_user=config['device42']['user'],
        auth_pass=config['device42']['pass'],
        node_classes_field=config['device42']['node_classes_field'],
        verify_cert=False
    )

    return node_classes

if __name__ == "__main__":
    retval = main()
    print('---')
    yaml.dump(retval, sys.stdout)
