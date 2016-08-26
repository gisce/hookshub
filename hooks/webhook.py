# -*- coding: utf-8 -*-
from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from json import dumps


class webhook(object):
    def __init__(self, data):
        self.json = data
        self.origin = 'webhook'

    @property
    def actions_path(self):
        return join(normpath(abspath(dirname(__file__))), self.origin)

    @property
    def event(self):
        return 'default_event'

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

    def get_exe_action(self, action):
        exe_path = join(self.actions_path, action)
        if action == self.event:
            return [exe_path, dumps(self.json), self.event]

    def get_test_action(self, action):
        return self.get_exe_action(action)
