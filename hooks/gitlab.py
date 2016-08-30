# -*- coding: utf-8 -*-
from webhook import webhook

EVENT_COMMENT = 'note'
EVENT_ISSUE = 'issue'
EVENT_MERGE_REQ = 'merge_request'
EVENT_PUSH_TAG = 'tag_push'
EVENT_PUSH = 'push'


class GitLabWebhook(webhook):

    def __init__(self, data):
        super(GitLabWebhook, self).__init__(data)
        self.origin = 'gitlab'

    def ssh_url(self):
        return self.json['repository']['git_ssh_url'] or None

    def http_url(self):
        return self.json['repository']['git_http_url'] or None

    @property
    def event(self):
        return self.json['object_kind']

    def repo_name(self):
        return self.json['repository']['name']

    def branch_name(self):
        try:
            if self.event == EVENT_PUSH:
                return self.json['ref'].split('/', 2)[-1]
            elif self.event == EVENT_MERGE_REQ:
                return self.json['object_attributes']['target_branch']
            elif self.event == EVENT_ISSUE:
                return self.json['object_attributes']['branch_name'] or 'None'
            elif self.event == EVENT_COMMENT:
                if 'issue' in self.json.keys():
                    return self.json['issue']['branch_name'] or 'None'
                elif 'merge_request' in self.json.keys():
                    return self.json['merge_request']['target_branch'] or 'None'
                else:
                    'None'
            else:
                return 'None'
        except KeyError:
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
            event == '{0}-{1}'.format(self.event, self.repo_name) or
            # If they start with {event}_{name}
            event.startswith('{0}_'.format(self.event)) or
            # If they are named after {event}
            event == '{0}'.format(self.event)
            ]
        return events
