#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

from json import loads, dumps
from subprocess import Popen, PIPE
from os.path import join

import sys
import tempfile
import shutil


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
url = payload['ssh_url'] or payload['http_url']
if not url:
    output = 'Failed to get URL (was it in payload?)'
    print (output)
    exit(-1)

repo_name = payload['repo_name']
repo_full_name = payload['repo_full_name']
branch_name = payload['branch_name']
output += ('Rebut event de <{}> |'.format(event))

conf_file = join(payload['actions_path'], 'conf.json')
# Directori on tenim la documentació en format html
with open(conf_file, 'r') as conf:
    json_conf = loads(conf.read())
    docs_path = json_conf['docs_path']
    token = json_conf['private_token']

docs_dir = 'powerp'

# Mirem de quina branca es tracta i actualitzem el directori del build:
#   Si es master el directori sera  /powerp/
#   Altrament el directori sera     /powerp_XXX/
#       on XXX es el nom de la branca
if branch_name != 'master' and branch_name != 'None':
    docs_dir += "_{}".format(branch_name)

docs_path = join(docs_path, docs_dir)

# Creem un directori temporal que guardarà les dades del clone
#   Per actualitzar la pagina de la documentacio
with TempDir() as temp:
    output += ('Creat Directori temporal: {} |'.format(temp.dir))

    # Primer clonem el repositori

    # Canviarà la forma de clonar segons tinguem o no branca:
    if branch_name != 'None':
        output += "Clonant el repositori '{0}', amb la branca '{1}' ...".format(
            repo_name, branch_name
        )
        command = 'git clone {0} --branch {1}'.format(url, branch_name)
    else:
        output += "Clonant el repositori '{0}' ...".format(repo_name)
        command = 'git clone {}'.format(url)

    new_clone = Popen(
        command.split(), cwd=temp.dir, stdout=PIPE, stderr=PIPE
    )
    out, err = new_clone.communicate()

    if new_clone.returncode != 0:
        # Could not clone >< => ABORT
        output += 'FAILED TO CLONE: {0}::{1}'.format(out, err)
        print(output)
        exit(-1)

    output += 'OK |'
    
    # Accedim al directori del clone utilitzant el nom del repositori

    clone_dir = join(temp.dir, repo_name)

    # Instalem dependencies

    output += 'Instal.lant dependencies...'
    command = 'pip install -r requirements.txt'
    dependencies = Popen(
        command.split(), cwd=clone_dir, stdout=PIPE, stderr=PIPE
    )
    out, err = dependencies.communicate()
    output += 'OK |'

    # Fem build al directori on tenim la pagina des del directori del clone

    command = 'mkdocs build -d {} --clean'.format(docs_path)
    output += 'Building mkdocs on {}...'.format(docs_path)
    new_build = Popen(
        command.split(), cwd=clone_dir, stdout=PIPE, stderr=PIPE
    )
    out, err = new_build.communicate()
    if new_build.returncode != 0:
        output += 'FAILED TO BUILD: {0}::{1}'.format(out, err)
        print(output)
        exit(-1)
    output += 'OK |'

print(output)
