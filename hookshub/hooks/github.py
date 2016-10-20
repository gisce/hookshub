# -*- coding: utf-8 -*-
from json import dumps, loads
from os.path import join
from subprocess import Popen, PIPE
from webhook import webhook

import requests
import sys

COMMIT_COMMENT = 'commit_comment'
EVENT_CREATE = 'create'
EVENT_DELETE = 'delete'
EVENT_DEPLOYMENT = 'deployment'
DEPLOYMENT_STATUS = 'deployment_status'
EVENT_FORK = 'fork'
EVENT_WIKI = 'gollum'
ISSUE_COMMENT = 'issue_comment'
EVENT_ISSUE = 'issues'
EVENT_MEMBER = 'member'
EVENT_MEMBERSHIP = 'membership'
EVENT_PAGE_BUILD = 'page_build'
PUBLIC_EVENT = 'public'
PULL_REQUEST = 'pull_request'
REVIEW_PR_COMMENT = 'pull_request_review_comment'
EVENT_PUSH = 'push'
EVENT_RELEASE = 'release'
EVENT_REPOSITORY = 'repository'
EVENT_STATUS = 'status'
EVENT_TEAM_ADD = 'team_add'
EVENT_WATCH = 'watch'


class GitHubWebhook(webhook):

    def __init__(self, data):
        super(GitHubWebhook, self).__init__(data)
        self.origin = 'github'

    @property
    def ssh_url(self):
        return self.json['repository']['ssh_url']

    @property
    def http_url(self):
        return self.json['repository']['clone_url']

    @property
    def repo_name(self):
        return self.json['repository']['name']

    @property
    def branch_name(self):
        branch = 'None'
        try:
            # Case 1: a ref_type indicates the type of ref.
            # This true for create and delete events.
            if self.event in [EVENT_CREATE, EVENT_DELETE]:
                if self.json['ref_type'] == 'branch':
                    branch = self.json['ref']
            # Case 2: a pull_request object is involved.
            # This is pull_request and pull_request_review_comment events.
            elif self.event in [PULL_REQUEST, REVIEW_PR_COMMENT]:
                # This is the SOURCE branch for the pull-request,
                #  not the source branch
                branch = self.json['pull_request']['head']['ref']

            elif self.event in [EVENT_PUSH]:
                # Push events provide a full Git ref in 'ref' and
                #  not a 'ref_type'.
                branch = self.json['ref'].split('/')[2]

        except KeyError:
            # If the self.json structure isn't what we expect,
            #  we'll live without the branch name
            pass
        return branch

    @property
    def target_branch_name(self):
        # Get TARGET branch from pull request
        if self.event in [PULL_REQUEST, REVIEW_PR_COMMENT]:
            return self.json['pull_request']['base']['ref']
        return 'None'

    @property
    def status(self):
        if self.event == EVENT_STATUS:
            return self.json['state']
        return 'None'

    @property
    def action(self):
        if self.event == PULL_REQUEST:
            return self.json['action']
        return 'None'

    @property
    def number(self):
        if self.event == PULL_REQUEST:
            return self.json['number']
        elif self.event == REVIEW_PR_COMMENT:
            return self.json['pull_request']['number']
        elif self.event in [EVENT_ISSUE, ISSUE_COMMENT]:
            return self.json['issue']['number']
        else:
            return 'None'

    @property
    def repo_id(self):
        return self.json['repository']['id']

    @property
    def repo_full_name(self):
        return self.json['repository']['full_name']

    @property
    def merged(self):
        if self.event == PULL_REQUEST:
            return self.json['pull_request']['merged']
        return False

    def get_exe_action(self, action, conf):
        exe_path = join(self.actions_path, action)
        json = {}
        # Action for 'push', 'pull_request' event
        #       on repository 'powerp-docs'
        if action.startswith('{}-powerp-docs'.format(EVENT_PUSH)) or\
                action.startswith('{}-powerp-docs'.format(PULL_REQUEST)):
            json.update({'token': conf['github_token']})
            json.update({'vhost_path': conf['vhost_path']})
            json.update({'port': conf['nginx_port']})
            json.update({'ssh_url': self.ssh_url})
            json.update({'http_url': self.http_url})
            json.update({'repo_name': self.repo_name})
            json.update({'repo_full_name': self.repo_full_name})
            json.update({'branch_name': self.branch_name})

            # If 'pull_request' event, we may add more params
            if action.startswith('{}-powerp-docs'.format(PULL_REQUEST)):
                json.update({'action': self.action})
                json.update({'number': self.number})

            # Return the params
            return [exe_path, dumps(json), self.event]
        else:
            return super(GitHubWebhook, self).get_exe_action(action, conf)

    @property
    def event(self):
        if 'commits' in self.json.keys():
            return 'push'

        elif 'master_branch' in self.json.keys():
            return 'create'

        elif 'ref_type' in self.json.keys():
            # This case must be under 'create'
            #   as it also has the 'ref_type' field on the payload
            return 'delete'

        elif 'deployment_status' in self.json.keys():
            return 'deployment_status'

        elif 'deployment' in self.json.keys():
            # This case must be under 'deployment_status'
            #   as it also has the 'deployment' field on the payload
            return 'deployment'

        elif 'forkee' in self.json.keys():
            return 'fork'

        elif 'pages' in self.json.keys():
            return 'gollum'

        elif 'issue' in self.json.keys():
            return ('issue_comment'
                    if self.json['action'] == 'created'
                    else 'issues')

        elif 'scope' in self.json.keys():
            return 'membership'

        elif 'build' in self.json.keys():
            return 'page_build'

        elif 'member' in self.json.keys():
            return 'member'

        elif 'comment' in self.json.keys():
            return ('pull_request_review_comment'
                    if 'pull_request' in self.json.keys()
                    else 'commit_comment'
                    )

        elif 'pull_request' in self.json.keys():
            return 'pull_request'

        elif 'release' in self.json.keys():
            return 'release'

        elif 'state' in self.json.keys():
            return 'status'

        elif 'team' in self.json.keys():
            # membership also uses 'team' in payload,
            # so this case may be under that case
            return 'team_add'

        elif 'organization' in self.json.keys():
            return 'repository'

        elif 'action' in self.json.keys():
            # Some other events use 'action' on its payload, so this case
            #   must be almost at the end where it's the last one to use it
            return 'watch'

        else:
            # As it has no specific payload, this one may be the last one
            return 'public'

    @property
    def event_actions(self):
        # We start with all actions that start with {event}
        # Then we filter them to not execute the actions for the same event
        #  with different repository.
        # Finally we filter what's left to not execute actions with the same
        #  repository but different branches
        events = super(GitHubWebhook, self).event_actions
        events = [
            event
            for event in events
            # If they start with {event}-{repository}-{branch}
            if event.startswith('{0}-{1}-{2}'.format(
                self.event, self.repo_name, self.branch_name
            )) or
            # If they start with {event}-{repository}_{name}
            event.startswith('{0}-{1}_'.format(self.event, self.repo_name)) or
            # If they are named after {event}-{repository}
            event == '{0}-{1}.py'.format(self.event, self.repo_name) or
            # If they start with {event}_{name}
            event.startswith('{0}_'.format(self.event)) or
            # If they are named after {event}
            event == '{0}.py'.format(self.event)
        ]
        return events


class GitHubUtil:
    @staticmethod
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
            output += 'FAILED TO CLONE: {}: | ' \
                      'Try to clone from https ...'.format(out)
            err = ':clone_repository_fail::{}'.format(err)
        return output, new_clone.returncode, err

    @staticmethod
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

    @staticmethod
    def docs_build(dir, target=None, clean=True):
        build_path = dir
        output = 'Building mkdocs from {} '.format(dir)
        command = 'mkdocs build '
        if target:
            build_path = target
            output += 'to {}...'.format(target)
            command += '-d {}'.format(target)
        if clean:
            command += ' --clean'
        try:
            new_build = Popen(
                command.split(), cwd=dir, stdout=PIPE, stderr=PIPE
            )
            out, err = new_build.communicate()
            if new_build.returncode != 0:
                output += 'FAILED TO BUILD: {0}::{1}'.format(out, err)
                return output, False
        except Exception as err:
            output += 'Build Failed with exception from Popen... {}'.format(err)
            return output, False

        return output, build_path

    @staticmethod
    def get_pr(token, repository, branch):
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
            my_prs = [pr for pr in prs if pr['head']['ref'] == branch]
            if my_prs:
                code = my_prs[0]
                output += 'MyPr: {}'.format(code['number'])
            else:
                output += 'OMITTING |'
                raise Exception('Could Not Get PULLS')
        except requests.ConnectionError as err:
            output = 'Failed to send comment to pull request -' \
                     ' Connection [{}]'.format(err)
        except requests.HTTPError as err:
            output = 'Failed to send comment to pull request -' \
                             ' HTTP [{}]'.format(err)
        except requests.RequestException as err:
            output = 'Failed to send comment to pull request -' \
                             ' REQUEST [{}]'.format(err)
        except Exception as err:
            output = 'Failed to send comment to pull request, ' \
                             'INTERNAL ERROR [{}]'.format(err)
        return code, output

    @staticmethod
    def post_comment_pr(token, repository, pr_num, message):
        import requests
        github_api_url = "https://api.github.com"
        # POST /repos/{:owner /:repo}/issues/{:pr_id}/comments
        req_url = '{0}/repos/{1}/issues/{2}/comments'.format(
            github_api_url, repository, pr_num
        )
        auth_token = 'token {}'.format(token)
        head = {'Authorization': auth_token}
        payload = {'body': message}
        code = 0
        try:
            post = requests.post(req_url, headers=head, json=payload)
            code = post.status_code
            text = post.text
        except requests.ConnectionError as err:
            text = 'Failed to send comment to pull request -' \
                             ' Connection [{}]'.format(err)
        except requests.HTTPError as err:
            text = 'Failed to send comment to pull request -' \
                             ' HTTP [{}]'.format(err)
        except requests.RequestException as err:
            text = 'Failed to send comment to pull request -' \
                             ' REQUEST [{}]'.format(err)
        except Exception as err:
            text = 'Failed to send comment to pull request, ' \
                             'INTERNAL ERROR [{}]'.format(err)
        return code, text
