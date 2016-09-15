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


def clone_on_dir(dir, branch, repository, url):
    output = "Clonant el repositori '{}'".format(repository)
    command = 'git clone {}'.format(url)
    if branch != 'None':
        output += ", amb la branca '{}'".format(branch)
        command += ' --branch {}'.format(branch)
        output += ' ... '
    new_clone = Popen(
        command.split(), cwd=dir, stdout=PIPE, stderr=PIPE
    )
    out, err = new_clone.communicate()
    if new_clone.returncode != 0:
        output += 'FAILED TO CLONE: {}: | Trying to clone from https ' \
                  '...'.format(out)
        sys.stderr.write(
            '[merge_request_lektor]:clone_repository_fail::{}'.format(err)
        )
    return output, new_clone.returncode


def pip_requirements(dir):
    output = 'Instal.lant dependencies...'
    command = 'pip install -r requirements.txt'
    dependencies = Popen(
        command.split(), cwd=dir, stdout=PIPE, stderr=PIPE
    )
    out, err = dependencies.communicate()
    if dependencies.returncode != 0:
        output += ' Couldn\'t install all dependencies '
    return output


def docs_build(dir, target, clean=True):
    build_path = dir
    output = 'Building mkdocs '
    command = 'mkdocs build '
    if target:
        build_path = target
        output += 'on {}...'.format(target)
        command += '-d {}'.format(target)
    if clean:
        command += ' --clean'
    new_build = Popen(
        command.split(), cwd=dir, stdout=PIPE, stderr=PIPE
    )
    out, err = new_build.communicate()
    if new_build.returncode != 0:
        output += 'FAILED TO BUILD: {0}::{1}'.format(out, err)
        print(output)
        exit(-1)
    return output, build_path


def github_get_pr(token, repository, branch):
    import requests
    output = 'Getting pull request... '
    if not repository or not branch:
        output += 'Repository and branch needed to get pull request!'
        return -1, output
    github_api_url = "https://api.github.com"
    auth_token = 'token {}'.format(token)
    head = {'Authorization': auth_token}
    # GET / repos / {:owner / :repo} / pulls
    req_url = '{0}/repos/{1}/pulls'.format(
        github_api_url, repository
    )
    code = -1
    try:
        pulls = requests.get(req_url, headers=head)
        if pulls.status_code != 200:
            output += 'OMITTING |'
            raise Exception('Could Not Get PULLS')
        prs = loads(pulls.text)
        # There are only opened PR, so the one that has the same branch name
        #   is the one we are looking for
        my_prs = [pr for pr in prs if pr['head']['ref'] == branch_name]
        if my_prs:
            code = my_prs[0]
            output += 'MyPr: {}'.format(code)
        else:
            output += 'OMITTING |'
            raise Exception('Could Not Get PULLS')
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
                         'INTERNAL ERROR [{}]'.format(err))
    return code, output


def github_post_comment_pr(token, repository, pr, message):
    import requests
    github_api_url = "https://api.github.com"
    # POST /repos/{:owner /:repo}/issues/{:pr_id}/comments
    req_url = '{0}/repos/{1}/issues/{2}/comments'.format(
        github_api_url, repository, pr['number']
    )
    auth_token = 'token {}'.format(token)
    head = {'Authorization': auth_token}
    payload = {'body': message}
    code = 0
    text = ''
    try:
        post = requests.post(req_url, headers=head, json=payload)
        code = post.status_code
        text = post.text
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
                         'INTERNAL ERROR [{}]'.format(err))
    return code, text

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
    out, code = clone_on_dir(temp.dir, branch_name, repo_name, url)
    output += out
    if code != 0:
        output += 'Clonant el repository desde http'
        url = payload['http_url']
        out, code = clone_on_dir(temp.dir, branch_name, repo_name, url)
        if code != 0:
            # Could not clone >< => ABORT
            sys.stderr.write('| Failed to get repository |')
            print(output)
            exit(-1)
    output += 'OK |'

    # Pendent de solucionar: No es pot entrar al virtualenv si amb el binari
    # especificat a dalt... A més l'interpret no pot canviar amb subprocess

    # output += 'Entrant al virtualenv: "docs" ... '
    # command = 'workon docs'
    # try:
    #     new_virtenv = Popen(
    #         command.split(), stdout=PIPE, stderr=PIPE
    #     )
    #     out, err = new_virtenv.communicate()
    #     virtenv = new_virtenv.returncode == 0
    #     if not virtenv:
    #         output += 'FAILED to enter virtualenv, installing on default env|'
    #     output += 'OK |'
    # except OSError as err:
    #     output += 'FAILED to enter virtualenv, installing on default env' \
    #               '\n {}|'.format(err)
    #     virtenv = False

    # Accedim al directori del clone utilitzant el nom del repositori

    clone_dir = join(temp.dir, repo_name)

    # Instalem dependencies

    output += '{} OK |'.format(pip_requirements(clone_dir))

    # Fem build al directori on tenim la pagina des del directori del clone

    out, target_build_path = (docs_build(clone_dir, docs_path))
    output += '{} OK |'.format(out)

    output += ' Writting comment on PR ...'

    # Construim el comentari:
    #   Docs path te /var/www/domain/URI
    base_url = docs_path.split('/', 3)[3]   # Kick out /var/www/
    base_uri = '{0}/powerp_{1}'.format(     # Get docs uri
        repo_name, branch_name
    )
    if port in ['80', '443']:
        res_url = '{0}/{1}'.format(base_url, base_uri)
    else:
        res_url = '{0}:{1}/{2}'.format(base_url, port, base_uri)
    comment = 'Documentation build URL: http://{}/'.format(res_url)

    # Necessitem agafar totes les pull request per trobar la nostra

    my_pr, out = github_get_pr(token, repo_full_name, branch_name)
    output += out

    # If getting pr fails, we ommit comment post
    if my_pr <= 0:
        print(output)
        exit(0)

        output += ' Writting comment on PR ...'
        # Necessitem agafar totes les pull request per trobar la nostra
        # GET / repos / {:owner / :repo} / pulls
        req_url = '{0}/repos/{1}/pulls'.format(
            http_url, repo_full_name
        )
        auth_token = 'token {}'.format(token)
        head = {'Authorization': auth_token}
        pulls = requests.get(req_url, headers=head)
        if pulls.status_code != 200:
            output += 'OMITTING |'
            raise Exception('Could Not Get PULLS')
        prs = loads(pulls.text)
        # There are only opened PR, so the one that has the same branch name
        #   is the one we are looking for
        my_prs = [pr for pr in prs if pr['head']['ref'] == branch_name]
        if my_prs:
            my_pr = my_prs[0]
            output += 'MyPr: {}'.format(my_pr)
        else:
            output += 'OMITTING |'
            raise Exception('Could Not Get PULLS')
        # Amb la pr, ja podem enviar el comentari
        # POST /repos/{:owner /:repo}/issues/{:pr_id}/comments
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
        comment = 'Documentation build URL: http://{}/'.format(res_url)
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
                         'INTERNAL ERROR [{}]'.format(err))

    # if virtenv:
    #     output += 'Deactivate virtualenv ...'
    #     command = 'deactivate'
    #     deact = Popen(
    #         command, cwd=clone_dir, stdout=PIPE, stderr=PIPE
    #     )
    #     out, err = deact.communicate()
    #     if deact.returncode != 0:
    #         output += 'FAILED TO DEACTIVATE: {0}::{1}'.format(out, err)
    #         print(output)
    #         exit(-1)
    #     output += 'OK |'

print(output)
