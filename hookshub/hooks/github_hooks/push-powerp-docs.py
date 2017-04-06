#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

from json import loads, dumps
from os.path import join
from hookshub.hooks.github import GitHubUtil as Util

import sys
import tempfile
import shutil
import os


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

# Get from env_vars
util_docs_path = '{0}/{1}'.format(payload['vhost_path'], repo_name)
token = payload['token']
port = payload['port']

docs_dir = 'powerp'

# Mirem de quina branca es tracta i actualitzem el directori del build:
#   Si es master el directori sera  /powerp/
#   Altrament el directori sera     /powerp_XXX/
#       on XXX es el nom de la branca
if branch_name != 'master' and branch_name != 'None':
    docs_dir += "_{}".format(branch_name)
else:
    docs_dir = 'master'

util_docs_path = join(util_docs_path, docs_dir)
ca_docs_path = join(util_docs_path, 'ca')
es_docs_path = join(util_docs_path, 'es')

# Creem un directori temporal que guardarà les dades del clone
#   Per actualitzar la pagina de la documentacio
with TempDir() as temp:
    output += ('Creat Directori temporal: {} |'.format(temp.dir))

    # Primer clonem el repositori
    out, code, err = Util.clone_on_dir(
        temp.dir, repo_name, url, branch=branch_name
    )
    output += out
    if code != 0:
        output += 'Clonant el repository desde http'
        url = payload['http_url']
        out, code, err2 = Util.clone_on_dir(
            temp.dir, repo_name, url, branch=branch_name
        )
        if code != 0:
            # Could not clone >< => ABORT
            sys.stderr.write(
                '| Failed to get repository {0};;{1}|'.format(err, err2)
            )
            print(output)
            exit(-1)
    output += ' OK |'

    # Pendent de solucionar: No es pot entrar al virtualenv si amb el binari
    # especificat a dalt... A més l'interpret no pot canviar amb subprocess

    # Accedim al directori del clone utilitzant el nom del repositori

    clone_dir = join(temp.dir, repo_name)

    # Crear Virtualenv en el directori temporal
    Util.create_virtualenv(temp.dir, branch_name)

    # Instalem dependencies

    output += Util.pip_requirements(clone_dir)

    # Fem build al directori on tenim la pàgina des del directori del clone

    #   Build en català

    out, target_build_path = (
        Util.docs_build(clone_dir, ca_docs_path, None, True)
    )
    # If build fails we can't continue
    if not target_build_path:
        output = '{} FAILED!\n{} |'.format(output, out)
        print (output)
        exit(1)
    output += '{} |'.format(out)

    #   Build en castellà

    out, target_build_path = (
        Util.docs_build(clone_dir, es_docs_path, 'mkdocs_es.yml', True)
    )
    # If build fails we can't continue
    if not target_build_path:
        output = '{} FAILED!\n{} |'.format(output, out)
        print(output)
        exit(1)
    output += '{} |'.format(out)

    # CP landing page (if exists)

    from os.path import isdir
    landing_dir = join(clone_dir, 'landing_page')
    if isdir(landing_dir):
        from distutils.dir_util import copy_tree as copy
        copy(landing_dir, util_docs_path)

    if docs_dir != 'master':
        output += ' Writting comment on PR ...'

        # Construim el comentari:
        #   Docs path te /var/www/domain/URI
        base_url = util_docs_path.split('/', 3)[3]   # Kick out /var/www/
        if port in ['80', '443']:
            res_url = '{0}/'.format(base_url)
        else:
            res_url = '{0}:{1}/'.format(base_url, port)
        comment = 'Documentation build URL:\nhttp://{}\n'.format(res_url)

        # Necessitem agafar totes les pull request per trobar la nostra

        my_pr, out = Util.get_pr(token, repo_full_name, branch_name)
        output += out

        # If getting pr fails, we ommit comment post
        if my_pr <= 0:
            print(output)
            exit(0)

        # Postejem el comentari

        post_code, post_text = Util.post_comment_pr(
            token, repo_full_name, my_pr['number'], comment
        )

        if post_code == 201:
            output += ' OK|'
        elif post_code == 0:
            output += ' Something went wrong |'
        else:
            output += 'Failed to write comment. ' \
                      'Server responded with {} |'.format(post_code)
            output += dumps(loads(post_text))
    
print(output)
