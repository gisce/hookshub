#!/usr/bin/python
# -*- coding: utf-8 -*-
from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from subprocess import Popen, PIPE
import sys


class webhook(object):
    def __init__(self, data, event):
        self.event = event
        self.json = data
        self.actions_path = join(
            normpath(abspath(dirname(__file__))), self.__class__.__name__
        )

    @property
    def origin(self):
        return 'Unknown'

    @property
    def actions(self):
        return [
            action
            for action in listdir(self.actions_path)
            if(
                isfile(join(self.actions_path, action))
            )]

    @property
    def event_actions(self):
        return [
               action
               for action in listdir(self.actions_path)
               if (
                    action.startswith(self.event) and
                    isfile(join(self.actions_path, action))
               )]

    def run_events(self):
        i = 1
        for action in self.event_actions:
            i += 1
            print ('Running: {0}/{1} - {2}'.format(
                i, len(self.event_actions), action)
            )
            action_path = join(self.actions_path, action)
            proc = Popen(
                [action_path, self.json, self.event],
                stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = proc.communicate()
            print ('ProcOut: {}'.format(stdout))
            print ('ProcErr: {}'.format(stderr))
            if proc.returncode != 0:
                print ('Failed!')
                return -1
        return 0

    def test_actions(self):
        print ('Origin: {}'.format(self.origin))
        print ('Event: {}'.format(self.event))
        print ('Actions: {}'.format(str(self.actions or 'None')))
        print ('Event actions: {}'.format(len(self.event_actions)))
        i = 0
        for action in self.event_actions:
            i += 1
            print ('Testing: {0} - {1}'.format(i, action))
            action_path = join(self.actions_path, action)
            proc = Popen(
                [action_path, self.json, self.event],
                stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = proc.communicate()
            print ('ProcOut: {}'.format(stdout))
            print ('ProcErr: {}'.format(stderr))
            if proc.returncode != 0:
                print ('Failed!')
                return -1
        return 0


def print_help():
    output = 'Calling structure:\n'
    output += '\t$ webhook [-h|--help] <data> <event> [-t|--test]\n'
    output += '\n> -h and -t are optional'
    output += '\n> by default and using -t data and event are mandatory'
    output += '\n> <data> contains a json string with all the hook payload'
    output += '\n> <event> contains a string with the event name of the request'
    print (output)


def print_bad_args():
    print('Not enough args or not correct, use -h or --help for more info')


test = False
data = False
event = False
myself = True
if len(sys.argv) == 1:
    print_bad_args()
elif len(sys.argv) >= 2:
    for arg in sys.argv:
        if myself:  # Skip call
            myself = False
        elif arg.startswith('-h') or arg.startswith('--help'):
            print_help()
            exit(0)
        elif not data:
            data = arg
        elif not event:
            event = arg
        elif arg.startswith('-t') or arg.startswith('--test'):
            test = True
        else:
            print_bad_args()
            exit(-1)
    if not data or not event:
        exit(-1)
    hook = webhook(data, event)
    if test:
        exit(hook.test_actions())
    exit(hook.run_events())
