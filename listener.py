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


def instancer(payload):
    if 'object_kind' in payload.keys():
        return gitlab(payload)
    elif 'hook' in payload.keys():
        return webhook(payload)
    else:
        return github(payload)


def get_args():
    first_arg = sys.argv[1]
    if first_arg.startswith('-t') or first_arg.startswith('--test'):
        if len(sys.argv) < 3:
            return json.loads('{"hook": "webhook", "test": "True"}'), 'default_event', True
    first = True
    payload = False
    event = False
    test = False
    for arg in sys.argv:
        if first:   # Skip executable argv
            first = False
        elif not payload:
            with open(arg, 'r') as jsf:
                payload = json.loads(jsf.read())
        elif arg.startswith('-t') or arg.startswith('--test'):
            test = True
        else:
            event = arg
    return payload, event, test


def run_event_actions(hook):
    i = 0
    for action in hook.event_actions:
        i += 1
        print ('[Running: <{0}/{1}> - {2}]'.format(
            i, len(hook.event_actions), action)
        )
        proc = Popen(
            hook.get_exe_action(action),
            stdout=PIPE, stderr=PIPE
        )
        stdout, stderr = proc.communicate()
        output = ''
        output += ('ProcOut: {}'.format(stdout))
        output += ('ProcErr: {}\n'.format(stderr))
        if proc.returncode != 0:
            print ('{}Failed!'.format(output))
            return -1
        print ('{}Success!'.format(output))
    return 0


def test_actions(hook):
    print ('[test:{0}]Origin: {0}'.format(hook.origin))
    print ('[test:{0}]Event: {1}'.format(hook.origin, hook.event))
    print ('[test:{0}]Actions: {1}'.format(hook.origin, str(hook.actions or 'None')))
    print ('[test:{0}]Event actions: {1}'.format(hook.origin, len(hook.event_actions)))
    i = 0
    for action in hook.event_actions:
        i += 1
        print ('[test:{0}][Running: <{1}/{2}> - {3}]'.format(
            hook.origin, i, len(hook.event_actions), action)
        )
        proc = Popen(
            hook.get_test_action(action),
            stdout=PIPE, stderr=PIPE
        )
        stdout, stderr = proc.communicate()
        output = ''
        output += ('[test:{0}>{1}:ProcOut]\n{2}'.format(hook.origin, action, stdout))
        output += ('[test:{0}>{1}:ProcErr]\n{2}'.format(hook.origin, action, stderr))
        if proc.returncode != 0:
            print ('[test:{0}>{1}]{2}Failed!'.format(hook.origin, action, output))
            return -1
        print ('{2}[test:{0}>{1}]Success!'.format(hook.origin, action, output))
    return 0

payload, event, test = get_args()
hook = instancer(payload)
if test:
    if event:   # If event was specified on args to test
        exit(test_actions(hook))
    else:       # Else we load all cases from test_data/{hook.origin}
        path = join(normpath(abspath(dirname(__file__))), 'test_data')
        path = join(path, hook.origin)
        if not isdir(path):
            print ('No test directory found in: {}'.format(path))
            exit()
        elif len(listdir(path)) == 0:
            print ('No test data found in: {}'.format(path))
        for test in listdir(path):
            test_path = join(path, test)
            with open(test_path, 'r') as test_json:
                data = json.loads(test_json.read())
                hook_test = instancer(data)
                test_actions(hook_test)
else:
    exit(run_event_actions(hook))
