# -*- coding: utf-8 -*-
from webhook import webhook


class GitLabWebhook(webhook):

    def __init__(self, data):
        super(GitLabWebhook, self).__init__(data)
        self.origin = 'gitlab'

    def ssh_url(self):
        return self.json['repository']['git_ssh_url'] or 'None'

    def http_url(self):
        return self.json['repository']['git_http_url'] or 'None'

    def event(self):
        return self.json['object_kind'] or 'None'

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
            event == '{0}-{1}'.format(self.event, self.repo_name) or
            # If they start with {event}_{name}
            event.startswith('{0}_'.format(self.event)) or
            # If they are named after {event}
            event == '{0}'.format(self.event)
            ]
        return events
