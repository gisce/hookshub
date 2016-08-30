# -*- coding: utf-8 -*-
from hooks.github import GitHubWebhook as github
from hooks.gitlab import GitLabWebhook as gitlab
from hooks.webhook import webhook
from subprocess import Popen, PIPE
import json


class HookListener(object):
    def __init__(self, payload_file, event):
        self.event = event
        self.payload = {}
        with open(payload_file, 'r') as jsf:
            self.payload = json.loads(jsf.read())

    @staticmethod
    def instancer(payload):
        if 'object_kind' in payload.keys():
            return gitlab(payload)
        elif 'hook' in payload.keys():
            return webhook(payload)
        else:
            return github(payload)

    def run_event_actions(self):
        hook = self.instancer(self.payload)
        i = 0
        for action in hook.event_actions:
            i += 1
            print ('{0}[Running: <{1}/{2}> - {3}]'.format(
                test_print, i, len(hook.event_actions), action)
            )
            args = hook.get_exe_action(action)
            proc = Popen(args, stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            output = ''
            output += ('[{0}]:ProcOut:\n{1}'.format(
                action, stdout
            ))
            output += ('[{0}]:ProcErr:\n{1}'.format(
                action, stderr
            ))
            if proc.returncode != 0:
                print ('{0}:{1}:{2}Failed!'.format(
                    test_print, action, output
                ))
                return -1
            print ('{0}:{1}:{2}Success!'.format(
                test_print, action, output
            ))
        return 0