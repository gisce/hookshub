#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

from json import loads, dumps
from os.path import join
from hookshub.hooks.github import GitHubUtil as Util

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

action = payload['action']
if action != 'opened':
    output = 'PR not ready, aborted ...'
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

repo_name = payload['repo_name']
repo_full_name = payload['repo_full_name']
branch_name = payload['branch_name']
output += ('Rebut event de <{}> |'.format(event))

# Get from env_vars
token = payload['token']
port = payload['port']

util_docs_path = '{0}/{1}'.format(
    payload['vhost_path'], repo_name
)

docs_path = '{0}/powerp_{2}'.format(
    util_docs_path, branch_name
)

with TempDir() as temp:
    output += ('Creat Directori temporal: {} |'.format(temp.dir))

    # Primer clonem el repositori
    out, code, err = Util.clone_on_dir(temp.dir, branch_name, repo_name, url)
    output += out
    if code != 0:
        output += 'Clonant el repository desde http'
        url = payload['http_url']
        out, code, err2 = Util.clone_on_dir(temp.dir, branch_name, repo_name,
                                            url)
        if code != 0:
            # Could not clone >< => ABORT
            sys.stderr.write(
                '| Failed to get repository {0};\n;{1}|'.format(err, err2)
            )
            print(output)
            exit(-1)
    output += 'OK |'

    # Pendent de solucionar: No es pot entrar al virtualenv si amb el binari
    # especificat a dalt... A més l'interpret no pot canviar amb subprocess

    # Accedim al directori del clone utilitzant el nom del repositori

    clone_dir = join(temp.dir, repo_name)

    # Instalem dependencies

    output += '{} OK |'.format(Util.pip_requirements(clone_dir))

    # Fem build al directori on tenim la pagina des del directori del clone

    out, target_build_path = (Util.docs_build(clone_dir, docs_path))
    # If build fails we can't continue
    if not target_build_path:
        output += '{} FAILED |'.format(out)
        print(output)
        exit(1)
    output += '{} OK |'.format(out)

    output += ' Writting comment on PR ...'

    # Construim el comentari:
    #   Docs path te /var/www/domain/URI
    base_url = util_docs_path.split('/', 3)[3]  # Kick out /var/www/
    base_uri = 'powerp_{}'.format(  # Get docs uri
        branch_name
    )
    if port in ['80', '443']:
        res_url = '{0}/{1}'.format(base_url, base_uri)
    else:
        res_url = '{0}:{1}/{2}'.format(base_url, port, base_uri)
    comment = 'Documentation build URL: http://{}/'.format(res_url)

    # Postejem el comentari

    post_code, post_text = Util.post_comment_pr(
        token, repo_full_name, pr_num, comment
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
