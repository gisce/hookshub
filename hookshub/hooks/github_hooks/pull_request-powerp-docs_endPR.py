#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

from json import loads, dumps
from os.path import join
from hookshub.hooks.github import GitHubUtil as Util
from subprocess import Popen, PIPE

import sys
import tempfile
import shutil

# This script is called whenever a PR is closed. Let it be the cases:
# - A PR has been merged (action= 'closed', merged= 'True')
# - A PR has been closed (action= 'closed', merged= 'False')


class TempDir(object):
    def __init__(self):
        self.dir = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.dir)


# Carrega dels arguments. Conte els detalls del event
def arguments():
    with open(sys.argv[1], 'r') as jsf:
        payload = loads(jsf.read())
    event = sys.argv[2]
    return payload, event

payload, event = arguments()

output = ''
http_url = "https://api.github.com"

action = payload['action']
if action != 'closed':
    output = 'PR is not "closed", aborting ...'
    print (output)
    exit(0)

pr_num = payload['number']
if not pr_num:
    output = 'Failed to get number (Is the PR ready?)'
    print (output)
    exit(-1)

url = payload['ssh_url'] or payload['http_url']
if not url:
    output = 'Failed to get URL (was it in payload?)'
    print (output)
    exit(-1)

closed = payload['closed']
repo_name = payload['repo_name']
repo_full_name = payload['repo_full_name']
branch_name = payload['branch_name']
output += ('Rebut event de <{}> |'.format(event))

# Get from env_vars
token = payload['token']
port = payload['port']


util_docs_path = '{0}/{1}/powerp_{2}'.format(
    payload['vhost_path'], repo_name, branch_name
)

docs_path = '{0}/{1}/master'.format(
    payload['vhost_path'], repo_name
)

ca_docs_path = '{0}/ca/'.format(
    docs_path
)
es_docs_path = '{0}/es/'.format(
    docs_path
)

output = 'Removing data on: {} ...'.format(util_docs_path)
command = 'rm -r {}'.format(util_docs_path)

delete = Popen(
    command.split(), stdout=PIPE, stderr=PIPE
)
out, err = delete.communicate()

if delete.returncode != 0:
    output += 'Failed to remove files! {}|'.format(out)
    output += 'Error on "rm -r": {}'.format(err)
    print(output)
    exit(-1)

output += 'Removed!|'

# Es pot fer despres de respondre:

# Si s'ha tencat sense mergejar, no actualitzem el build
#   Altrament fem build de master abans de borrar la PR
if not closed:
    with TempDir() as temp:
        output += ('Creat Directori temporal: {} |'.format(temp.dir))

        # Primer clonem el repositori
        out, code, err = Util.clone_on_dir(temp.dir, repo_name, url)
        output += out
        if code != 0:
            output += 'Clonant el repository desde http'
            url = payload['http_url']
            out, code, err2 = Util.clone_on_dir(temp.dir, repo_name, url)
            if code != 0:
                # Could not clone >< => ABORT
                sys.stderr.write(
                    '| Failed to get repository {0};\n;{1}|'.format(err, err2)
                )
                print(output)
                exit(-1)
        output += 'OK |'
        # Accedim al directori del clone utilitzant el nom del repositori

        clone_dir = join(temp.dir, repo_name)

        # Instalem dependencies

        output += '{} OK |'.format(Util.pip_requirements(clone_dir))

        # Exportem PYTHONPATH

        output += '{} OK |'.format(Util.export_pythonpath(clone_dir))

        # Fem build al directori on tenim la pagina des del directori del clone
        #   Build en català
        out, target_build_path = (
            Util.docs_build(clone_dir, ca_docs_path, None, True)
        )
        if not target_build_path:
            output += '{} FAILED |'.format(out)
        output += '{} OK |'.format(out)

        #   Build en castellà
        out, target_build_path = (
            Util.docs_build(clone_dir, es_docs_path, 'mkdocs_es.yml', True)
        )
        if not target_build_path:
            output += '{} FAILED |'.format(out)
        output += '{} OK |'.format(out)

print(output)
