#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from subprocess import Popen, PIPE
from os.path import join
from json import loads
from tempfile import mkdtemp
from shutil import rmtree
from hookshub.hooks.gitlab import GitLabUtil as Util
from hookshub import utils
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

# Get your GitLab's domain's URL
# 'http:'/''/'url'/
http_res = payload['http_url'].split('/')
http_url = http_res[0]
if http_url == 'http:':
    http_url += '//'
    http_url += http_res[1] if http_res[1] != '' else http_res[2]

# Check for URL in payload

url = payload['ssh_url']
ssh_found = True
if not url:
    # Not ssh_url? Get it from Http
    ssh_found = False
    url = payload['http_url']
    if not url:
        output = 'Failed to get URL (was it in payload?)'
        print (output)
        exit(-1)

repo_name = payload['repo_name']        # Source Repository Name
source_branch = payload['branch_name']  # Source branch
project_id = payload['project_id']      # Source Project ID
index_id = payload['index_id']          # item PR id
merge_id = payload['object_id']         # action PR id
state = payload['state']                # Merge Request State
merged = state == 'merged'
# Get from env_vars
lektor_path = '{0}/{1}'.format(payload['vhost_path'], repo_name)
token = payload['token']
port = payload['port']

branch_path = '{0}/branch/{1}'.format(lektor_path, source_branch)
mr_path = '{}/PR/'.format(lektor_path)
master_path = ''
if merged:
    master_path = '{0}/{1}'.format(lektor_path, 'master')

with TempDir() as tmp:
    tmp_dir = tmp.dir
    output += ('Creat Directori temporal: {} |'.format(tmp_dir))

    branch = 'None' if merged else source_branch
    out, code, err = Util.clone_on_dir(tmp_dir, branch, repo_name, url)

    output += "Clonant desde ssh_url... "
    if code != 0:
        output += out
        err2 = None
        if ssh_found:
            output += "Clonant desde http_url... "
            out, code, err2 = Util.clone_on_dir(
                tmp_dir, branch, repo_name, url
            )
        if not ssh_found or not err2:
            sys.stderr.write('|(ssh) Failed to get repository {}|'.format(err))
            if err2:
                sys.stderr.write('|(http) Failed to get repository {}|'.format(err2))
            output += out
            print(output)
            exit(-1)

    output += 'OK |'

    clone_dir = join(tmp_dir, repo_name)

    utils.create_virtualenv(name='lektor', dir=tmp_dir)

    output += 'Instal.lant dependencies...'
    output += '{} DONE |'.format(utils.pip_requirements(clone_dir))

    # Fem build al directori on tenim la pagina des del directori del clone
    path = master_path if merged else branch_path
    out, ret_path = utils.lektor_build(
        clone_dir, path, 'gisce.net-lektor'
    )
    output += out
    if not ret_path or path != ret_path:
        print (output)
        exit(-1)
    output += 'OK |'

    # If merged, there is no comment to be done, so we end
    if merged:
        print(output)
        exit(0)

    # SYMLINK built page to /PR/ Directory
    # Create the directory for /PR/
    #   |-> Instead of check and create, we create it and if it's already
    #       created nothing may change
    command = 'mkdir -p {}'.format(mr_path)
    output += 'Making dir {} ...'.format(mr_path)
    mkdir = Popen(
        command.split(), stdout=PIPE, stderr=PIPE
    )
    out, err = mkdir.communicate()

    # Remove old /PR/{id} dir, with old copies
    #   |-> As before, if the dir does not exist, the command will fail, but
    #       Nothing may change
    command = 'rm -r {0}{1}'.format(mr_path, index_id)
    output += 'Removing dir {0}{1} ...'.format(mr_path, index_id)
    rmdir = Popen(
        command.split(), stdout=PIPE, stderr=PIPE
    )
    out, err = rmdir.communicate()

    # Build the SymLing from the built path (branch_path) to the PR/{id} path
    # Created from the (cwd=) mr_path where the directory {id} is

    command = 'ln -s {0} {1}'.format(branch_path, index_id)
    output += 'Symbolic link from data in {0} to {1} ...'.format(
        branch_path, index_id
    )
    sym_link = Popen(
        command.split(), cwd=mr_path, stdout=PIPE, stderr=PIPE
    )
    out, err = sym_link.communicate()

    if sym_link.returncode != 0:
        output += 'FAILED TO SYMLINK! - Output::{0}'.format(out)
        sys.stderr.write(
            '[merge_request_lektor]:sym_link_error:{}'.format(err)
        )
    output += 'OK |'

    # After the Build and the SymLink => Comment on MR

    # POST /projects/:id/merge_requests/:merge_request_id/notes
    req_url = '{0}/api/v3/projects/{1}/merge_requests/{2}/notes'.format(
        http_url, project_id, merge_id
    )

    # Build the comment to be posted

    # Lektor path has /var/www/domain
    base_url = lektor_path.split('/', 3)[3]       # Kick out /var/www/
    base_uri = 'branch/{0}'.format(source_branch)
    if port in ['80', '443']:
        res_url_branch = '{0}/{1}'.format(base_url, base_uri)
    else:
        res_url_branch = '{0}:{1}/{2}'.format(base_url, port, base_uri)
    base_uri = 'PR/{0}'.format(index_id)   # Get build uri
    if port in ['80', '443']:
        res_url_request = '{0}/{1}'.format(base_url, base_uri)
    else:
        res_url_request = '{0}:{1}/{2}'.format(base_url, port, base_uri)
    comment = 'Branch URL: http://{0}/\nPR URL: http://{1}/'.format(
        res_url_branch, res_url_request
    )
    output += 'Build comment as \n{} | '.format(comment)
    code, out = Util.post_comment_mr(
        http_url, token, project_id, merge_id, comment
    )
    if code != 201:
        output += out
        sys.stderr.write("Could not POST comment on MR! {}|".format(code))
        print(output)
        exit(0)
    else:
        output += "Posted Comment Successfully"

print(output)
