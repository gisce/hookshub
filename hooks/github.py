# -*- coding: utf-8 -*-
from webhook import webhook


class GitHubWebhook(webhook):

    def __init__(self, data):
        super(GitHubWebhook, self).__init__(data)
        self.origin = 'github'

    def ssh_url(self):
        return self.json['repository']['ssh_url'] or 'None'

    def http_url(self):
        return self.json['repository']['clone_url'] or 'None'

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

        elif ['comment', 'pull_request'] in self.json.keys():
            return 'pull_request_review_comment'

        elif 'comment' in self.json.keys():
            # This case must be under 'pull_request_review_comment'
            #   as it also has the 'comment' field on the payload
            return 'commit_comment'

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

        elif 'action' in self.json.keys():
            # Some other events use 'action' on its payload, so this case
            #   must be almost at the end where it's the last one to use it
            return 'watch'

        elif 'repository' in self.json.keys():
            # As almost every other event uses 'repository' this may be the
            #  last one that uses it
            return 'repository'

        else:
            # As it has no specific payload, this one may be the last one
            return 'public'
