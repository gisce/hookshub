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

# Get from env_vars
docs_path = '{0}/{1}'.format(payload['vhost_path'], repo_name)
token = payload['token']
port = payload['port']

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
        output += 'FAILED TO CLONE: {}: | Trying to clone from https ' \
                  '...'.format(out)
        sys.stderr.write(
            '[merge_request_lektor]:clone_repository_fail::{}'.format(err)
        )
        url = payload['http_url']
        if branch_name != 'None':
            output += "Clonant el repositori '{0}', amb la branca '{1}' " \
                      "...".format(repo_name, branch_name)
            command = 'git clone {0} --branch {1}'.format(url, branch_name)
        else:
            output += "Clonant el repositori '{0}' ...".format(repo_name)
            command = 'git clone {}'.format(url)

        new_clone = Popen(
            command.split(), cwd=temp.dir, stdout=PIPE, stderr=PIPE
        )
        out, err = new_clone.communicate()

        if new_clone.returncode != 0:
            print(output)
            exit(-1)

    output += 'OK |'

    output += 'Entrant al virtualenv: "docs" ... '
    command = 'workon docs'
    try:
        new_virtenv = Popen(
            command.split(), stdout=PIPE, stderr=PIPE
        )
        out, err = new_virtenv.communicate()
        virtenv = new_virtenv.returncode == 0
        if not virtenv:
            output += 'FAILED to enter virtualenv, installing on default env |'
        output += 'OK |'
    except OSError as err:
        output += 'FAILED to enter virtualenv, installing on default env' \
                  '\n {}|'.format(err)
        virtenv = False

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

    try:
        import requests
        output += ' Writting comment on PR ...'
        # Necessitem agafar totes les pull request per trobar la nostra
        # GET / repos / {:owner / :repo} / pulls
        req_url = '{0}/repos/{1}/pulls'.format(
            http_url, repo_full_name
        )
        head = {'Authorization': 'token {}'.format(token)}
        pulls = requests.get(req_url, headers=head)
        if pulls.status_code != 200:
            raise Exception('Could Not Get PULLS, omitting comment |')
        prs = loads(pulls.text)
        # There are only opened PR, so the one that has the same branch name
        #   is the one we are looking for
        my_pr = [pr for pr in prs if pr['head']['ref'] == branch_name][0]
        # Amb la pr, ja podem enviar el comentari
        # POST /repos/{:owner /:repo}/pulls/{:pr_id}/comments
        req_url = '{0}/repos/{1}/issues/{2}/comments'.format(
            http_url, repo_full_name, my_pr['number']
        )
        # Docs path te /var/www/domain/URI
        base_url = docs_path.split('/', 3)[3]   # Kick out /var/www/
        base_uri = '{0}/powerp_{1}'.format(     # Get docs uri
            repo_name, branch_name
        )
        if port in ['80', '443']:
            res_url = '{0}/{1}'.format(base_url, base_uri)
        else:
            res_url = '{0}:{1}/{2}'.format(base_url, port, base_uri)
        comment = 'Documentation build URL: http://{}/'.format(
            docs_url
        )
        payload = {'body': comment}
        post = requests.post(req_url, headers=head, json=payload)
        output += 'URL: {}\n'.format(req_url)
        output += 'HEAD: {}\n'.format(head)
        output += 'DATA: {}\n'.format(payload)

        if post.status_code == 201:
            output += ' OK|'
        else:
            output += 'Failed to write comment. ' \
                      'Server responded with {} |'.format(post.status_code)
            output += dumps(loads(post.text))

    except requests.ConnectionError as err:
        sys.stderr.write('Failed to send comment to pull request -'
                         ' Connection [{}]'.format(err))
    except requests.HTTPError as err:
        sys.stderr.write('Failed to send comment to pull request -'
                         ' HTTP [{}]'.format(err))
    except requests.RequestException as err:
        sys.stderr.write('Failed to send comment to pull request -'
                         ' REQUEST [{}]'.format(err))
    except Exception as err:
        sys.stderr.write('Failed to send comment to pull request, '
                         'INTERNAL ERROR {}|'.format(err))

    if virtenv:
        output += 'Deactivate virtualenv ...'
        command = 'deactivate'
        deact = Popen(
            command, cwd=clone_dir, stdout=PIPE, stderr=PIPE
        )
        out, err = deact.communicate()
        if deact.returncode != 0:
            output += 'FAILED TO DEACTIVATE: {0}::{1}'.format(out, err)
            print(output)
            exit(-1)
        output += 'OK |'

print(output)
