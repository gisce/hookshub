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
