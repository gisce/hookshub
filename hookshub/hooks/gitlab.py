# -*- coding: utf-8 -*-
from webhook import webhook
from json import dumps
from subprocess import Popen, PIPE

import requests
# GitLab events
#   For more information about GitLab events, check the official docs:
# https://gitlab.com/gitlab-org/gitlab-ce/blob/master/doc/web_hooks/web_hooks.md

EVENT_COMMENT = 'note'
EVENT_ISSUE = 'issue'
EVENT_MERGE_REQ = 'merge_request'
EVENT_PUSH_TAG = 'tag_push'
EVENT_PUSH = 'push'


class GitLabWebhook(webhook):

    def __init__(self, data):
        super(GitLabWebhook, self).__init__(data)
        self.origin = 'gitlab'

    @property
    def ssh_url(self):
        if self.event == EVENT_MERGE_REQ:
            return self.json['object_attributes']['source']['git_ssh_url']
        elif self.event == EVENT_COMMENT \
                and 'merge_request' in self.json.keys():
                    return self.json['merge_request']['source']['git_ssh_url']
        return self.json['repository']['git_ssh_url']

    @property
    def http_url(self):
        if self.event == EVENT_MERGE_REQ:
            return self.json['object_attributes']['source']['git_http_url']
        elif self.event == EVENT_COMMENT \
                and 'merge_request' in self.json.keys():
                    return self.json['merge_request']['source']['git_http_url']
        return self.json['repository']['git_http_url']

    @property
    def event(self):
        return self.json['object_kind']

    @property
    def repo_name(self):
        if self.event == EVENT_MERGE_REQ:
            return self.json['object_attributes']['source']['name']
        elif self.event == EVENT_COMMENT \
                and 'merge_request' in self.json.keys():
                    return self.json['merge_request']['source']['name']
        return self.json['repository']['name']

    @property
    def branch_name(self):
        branch = 'None'
        try:
            if self.event == EVENT_PUSH:
                branch = self.json['ref'].split('/', 2)[-1]
            elif self.event == EVENT_MERGE_REQ:
                branch = self.json['object_attributes']['source_branch']
            elif self.event == EVENT_ISSUE:
                branch = self.json['object_attributes']['branch_name'] or 'None'
            elif self.event == EVENT_COMMENT:
                if 'issue' in self.json.keys():
                    branch = self.json['issue']['branch_name'] or 'None'
                elif 'merge_request' in self.json.keys():
                    branch = self.json['merge_request']['source_branch']
        except KeyError:
            pass
        return branch

    @property
    def target_branch_name(self):
        if self.event == EVENT_MERGE_REQ:
            return self.json['object_attributes']['target_branch']
        elif self.event == EVENT_COMMENT \
                and 'merge_request' in self.json.keys():
            return self.json['merge_request']['target_branch']
        return 'None'

    @property
    def index_id(self):
        if self.event == EVENT_PUSH or self.event == EVENT_PUSH_TAG:
            return None
        if self.event == EVENT_COMMENT and 'merge_request' in self.json.keys():
            return self.json['merge_request']['iid']
        return self.json['object_attributes']['iid']

    @property
    def object_id(self):
        if self.event == EVENT_PUSH or self.event == EVENT_PUSH_TAG:
            return None
        if self.event == EVENT_COMMENT and 'merge_request' in self.json.keys():
            return self.json['merge_request']['id']
        return self.json['object_attributes']['id']

    @property
    def project_id(self):
        if self.event == EVENT_ISSUE:
            return None
        elif self.event == EVENT_MERGE_REQ:
            return self.json['object_attributes']['source_project_id']
        elif self.event == EVENT_COMMENT \
                and 'merge_request' in self.json.keys():
            return self.json['merge_request']['source_project_id']
        return self.json['project_id']

    @property
    def target_project_id(self):
        if self.event == EVENT_MERGE_REQ:
            return self.json['object_attributes']['target_project_id']
        elif self.event == EVENT_COMMENT \
                and 'merge_request' in self.json.keys():
            return self.json['merge_request']['target_project_id']
        return None

    @property
    def state(self):
        if self.event == EVENT_MERGE_REQ or self.event == EVENT_ISSUE:
            return self.json['object_attributes']['state']
        elif self.event == EVENT_COMMENT \
                and 'merge_request' in self.json.keys():
            return self.json['merge_request']['state']
        elif self.event == EVENT_COMMENT and 'issue' in self.json.keys():
            return self.json['issue']['state']
        return 'None'

    @property
    def event_actions(self):
        # We start with all actions that start with {event}
        # Then we filter them to not execute the actions for the same event
        #  with different repository.
        # Finally we filter what's left to not execute actions with the same
        #  repository but different branches
        events = super(GitLabWebhook, self).event_actions
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

    def get_exe_action(self, action, conf):
        json = {}
        json.update({'token': conf['gitlab_token']})
        args = super(GitLabWebhook, self).get_exe_action(action, conf)
        if action.startswith(EVENT_MERGE_REQ):
            json.update({'vhost_path': conf['vhost_path']})
            json.update({'port': conf['nginx_port']})
            json.update({'ssh_url': self.ssh_url})
            json.update({'http_url': self.http_url})
            json.update({'repo_name': self.repo_name})
            json.update({'branch_name': self.branch_name})
            json.update({'index_id': self.index_id})
            json.update({'object_id': self.object_id})
            json.update({'project_id': self.project_id})
            json.update({'state': self.state})
            args = [args[0], dumps(json)]
        return args

class GitLabUtil:
    @staticmethod
    def clone_on_dir(dir, branch, repository, url):
        """
        :param dir: Directory where the clone will be applied. This may exist
            or it'll throw an exception.
            :type: String
        :param branch: Branch to clone from the repository. If cloning master,
            this may have the value 'None'
            :type: String
        :param repository: Repository to clone from. Cannot be None
            :type: String
        :param url: URL used to clone the repository
            :type: String
        :return: Returns the log output, the return code from the clone and the
            clone error log.
            :rtype: Tuple<String,Int,String>
        """
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
            output += 'FAILED TO CLONE: {} | ' \
                      'Try cloning from https ...'.format(err)
            err = ':clone_repository_fail::{}'.format(err)
        return output, new_clone.returncode, err

    @staticmethod
    def pip_requirements(dir):
        """
        Installs all the requirements from the requirements.txt in the specified
        directory. If no virtualenv is set previously for the Popen, they will
        be installed in the user's python directory
        :param dir: Directory where the requirements.txt is found. Used to call
            Popen with the pip install.
            :type: String
        :return: Output with the log. Does not include any of the pip install
            output or error prints.
        :rtype: String
        """
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
    def lektor_build(dir, target=None, project=None):
        """
        :param dir: Directory used to call the build. This MUST exist.
            :type:  String
        :param target: Directory to build to. If not set or None, the target
            build is the default one, that is the same as 'dir'
            :type:  String
        :param project: Project to find in the directory, used by lektor command
            May be None, and is not used if in the right directory.
            :type:  String
        :return: An output log with some annotations and the output and error
            log from the lektor build call. And a String containing the path
            where the docs have been built
            :type: Tuple<String, String>
        """
        build_path = dir
        output = 'Building lector from {} '.format(dir)
        command = 'lektor '
        if project:
            output += 'for the project {} '.format(project)
            command += '--project {}'.format(project)
        command += ' build'
        if target:
            build_path = target
            output += 'to {}...'.format(target)
            command += ' -O {}'.format(target)
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
    def post_comment_mr(http_url, token, project, merge_num, message):
        """
        :param http_url: GitLab URL, used as parameter because GitLab is for EE
            So the URL may change.
            :type:  String
        :param token:   GitLab Token used for the HTTP Requests
            :type:  String
        :param project: The Project ID where the MR belongs to
            :type:  String
        :param merge_num: The MR number or ID for which we may send the comment
            :type:  Int
        :param message: The message to write the comment
            :type:  String
        :return: The HTTP Response's status code. If it works well, this may
            return the status code 201 (Created). If it doesn't, this may
            return the code 0 along with a text with the error found.
        :rtype: Tuple<Int,String>
        """
        # POST /projects/:id/merge_requests/:merge_request_id/notes
        req_url = '{0}/api/v3/projects/{1}/merge_requests/{2}/notes'.format(
            http_url, project, merge_num
        )
        head = {'PRIVATE-TOKEN': token}
        payload = {'body': message}
        code = 0
        try:
            post = requests.post(req_url, headers=head, json=payload)
            code = post.status_code
            text = post.text
            if code != 201:
                raise Exception(
                    "Bad return code, returned text: \n[{}]\n".format(
                        text
                    )
                )
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
