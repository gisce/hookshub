#!/usr/bin/python
# -*- coding: utf-8 -*-
from hooks.github import GitHubWebhook as github
from hooks.gitlab import GitLabWebhook as gitlab
from hooks.webhook import webhook
from subprocess import Popen, PIPE
from os.path import abspath, normpath, dirname, join, isfile, isdir
from os import listdir
import sys
import json


class hook_listener(object):
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

    def get_args(self):
        return self.payload, self.event

    def run_event_actions(self, test):
        hook = self.instancer(self.payload)
        test_print = ''
        if test:
            test_print = '[test:{0}]'.format(hook.origin)
            print ('{0}Origin: {1}'.format(test_print, hook.origin))
            print ('{0}Event: {1}'.format(test_print, hook.event))
            print ('{0}Actions: {1}'.format(
                test_print, str(hook.event_actions or 'None')
            ))
        i = 0
        for action in hook.event_actions:
            i += 1
            print ('{0}[Running: <{1}/{2}> - {3}]'.format(
                test_print, i, len(hook.event_actions), action)
            )
            proc = Popen(
                hook.get_exe_action(action),
                stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = proc.communicate()
            output = ''
            output += ('{0}:{1}:ProcOut:\n{2}'.format(
                test_print,action, stdout
            ))
            output += ('{0}:{1}:ProcErr:\n{2}'.format(
                test_print, action, stderr
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