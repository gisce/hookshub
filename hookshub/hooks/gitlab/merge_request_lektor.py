#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from subprocess import Popen, PIPE
from os.path import join
from json import loads
from tempfile import mkdtemp
from shutil import rmtree
import sys


class TempDir(object):
    def __init__(self):
        self.dir = mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rmtree(self.dir)


def arguments():
    with open(sys.argv[1], 'r') as jsf:
        payload = loads(jsf.read())
    return payload

output = ''
out = ''
payload = arguments()
url = payload['ssh_url'] or payload['http_url']
if not url:
    output = 'Failed to get URL (was it in payload?)'
    print (output)
    exit(-1)

repo_name = payload['repo_name']
source_branch = payload['branch_name']    # Source branch

lektor_path = 'tmp/builtin/lektor'

if source_branch != 'master' and source_branch != 'None':
    lektor_path += '_{}'.format(source_branch)

with TempDir() as tmp:
    tmp_dir = tmp.dir
    output += ('Creat Directori temporal: {} |'.format(tmp_dir))
    command = ''
    if source_branch != 'None':
        output += "Clonant el repositori '{0}', amb la branca '{1}' ...".format(
            repo_name, source_branch
        )
        command = 'git clone {0} --branch {1}'.format(url, source_branch)
    else:
        output += "Clonant el repositori '{0}' ...".format(repo_name)
        command = 'git clone {}'.format(url)

    new_clone = Popen(
        command.split(), cwd=tmp_dir, stdout=PIPE, stderr=PIPE
    )
    out, err = new_clone.communicate()

    if new_clone.returncode != 0:
        # Could not clone >< => ABORT
        output += 'FAILED TO CLONE: {0}:{1}'.format(out)
        print(output)
        sys.stderr.write(
            '[merge_request_lektor]:clone_repository_fail::{}'.format(err)
        )
        exit(-1)

    output += 'OK |'

    clone_dir = join(tmp_dir, repo_name)

    output += 'Creant virtualenv: {} ... '.format(tmp_dir)
    command = 'mkvirtualenv {}'.format(tmp_dir)
    try:
        new_virtenv = Popen(
            command.split(), cwd=clone_dir, stdout=PIPE, stderr=PIPE
        )
        out, err = new_virtenv.communicate()
        virtenv = new_virtenv.returncode == 0
        if not virtenv:
            output += 'FAILED to create virtualenv, installing on default env |'
        output += 'OK |'
    except OSError as err:
        output += 'FAILED to create virtualenv, installing on default env |'
        virtenv = False
    output += 'Instal.lant dependencies...'
    command = 'pip install -r requirements.txt'
    dependencies = Popen(
        command.split(), cwd=clone_dir, stdout=PIPE, stderr=PIPE
    )
    out, err = dependencies.communicate()
    output += 'OK |'

    # Fem build al directori on tenim la pagina des del directori del clone

    command = 'lektor --project gisce.net-lektor build -O {}'.format(lektor_path)
    output += 'Building lektor on {}...'.format(lektor_path)
    new_build = Popen(
        command.split(), cwd=clone_dir, stdout=PIPE, stderr=PIPE
    )
    out, err = new_build.communicate()
    if new_build.returncode != 0:
        out = 'FAILED TO BUILD! - Output::{0}'.format(out)
        sys.stderr.write(
            '[merge_request_lektor]:build_lektor_error:{}'.format(err)
        )
    output += 'OK |'

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

        command = 'rmvirtualenv {}'.format(tmp_dir)
        output += 'Removing virtual environment: {} ...'.format(tmp_dir)
        rm_virt = Popen(
            command.split(), cwd=clone_dir, stdout=PIPE, stderr=PIPE
        )
        out, err = rm_virt.communicate()
        if rm_virt.returncode != 0:
            output += 'FAILED TO REMOVE VIRTUALENV: {0}::{1}'.format(out, err)
            print(output)
            exit(-1)
        output += 'OK |'

print(output)
print(out)