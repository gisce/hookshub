#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

from json import loads
from hookshub.hooks.github import GitHubUtil as Util

import sys
from os import system as call

# This script is called whenever a PR is closed. Let it be the cases:
# - A PR has been merged (action= 'closed', merged= 'True')
# - A PR has been closed (action= 'closed', merged= 'False')


# Carrega dels arguments. Conte els detalls del event
def arguments():
    with open(sys.argv[1], 'r') as jsf:
        payload = loads(jsf.read())
    event = sys.argv[2]
    return payload, event


payload, event = arguments()

output = ''

action = payload['action']
if action != Util.actions['ACT_CLOSED']:
    output = 'PR is "{}", not "{}", aborting ...'.format(
        action, Util.actions['ACT_CLOSED']
    )
    print (output)
    exit(0)

repo_name = payload['repo_name']
branch_name = payload['branch_name']
output += ('Rebut event de <{}> |'.format(event))


util_docs_path = '{0}/{1}/powerp_{2}'.format(
    payload['vhost_path'], repo_name, branch_name
)

output = 'Removing data on: {} ...'.format(util_docs_path)
command = 'rm -r {}'.format(util_docs_path)

if call(command) != 0:
    output += 'Failed to remove files! |'
    print(output)
    exit(-1)

output += 'Removed!|'
print(output)
