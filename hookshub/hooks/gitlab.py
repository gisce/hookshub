# -*- coding: utf-8 -*-
from webhook import webhook
from json import dumps

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
        return self.json['repository']['git_ssh_url']

    @property
    def http_url(self):
        return self.json['repository']['git_http_url']

    @property
    def event(self):
        return self.json['object_kind']

    @property
    def repo_name(self):
        return self.json['repository']['name']

    @property
    def branch_name(self):
        branch = 'None'
        try:
            if self.event == EVENT_PUSH:
                branch = self.json['ref'].split('/', 2)[-1]
            elif self.event == EVENT_MERGE_REQ:
                branch = self.json['object_attributes']['target_branch']
            elif self.event == EVENT_ISSUE:
                branch = self.json['object_attributes']['branch_name'] or 'None'
            elif self.event == EVENT_COMMENT:
                if 'issue' in self.json.keys():
                    branch = self.json['issue']['branch_name'] or 'None'
                elif 'merge_request' in self.json.keys():
                    branch = self.json['merge_request']['target_branch']
        except KeyError:
            pass
        return branch

    @property
    def source_branch_name(self):
        if self.event == EVENT_MERGE_REQ:
            return self.json['merge_request']['target_branch']
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

    def get_exe_action(self, action):
        args = super(GitLabWebhook, self).get_exe_action(action)
        if action.startswith(EVENT_MERGE_REQ):
            json = {}
            json.update({'ssh_url': self.ssh_url})
            json.update({'http_url': self.http_url})
            json.update({'repo_name': self.repo_name})
            json.update({'branch_name': self.source_branch_name})
            args = [args[0], dumps(json)]
        return args