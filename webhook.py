#!/usr/bin/python
# -*- coding: utf-8 -*-
from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from subprocess import Popen, PIPE


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
                return False
        return True
