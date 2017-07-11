# -*- coding: utf-8 -*-
from os.path import abspath, normpath, dirname, join, isfile, isdir
from os import listdir
from json import dumps


class webhook(object):
    def __init__(self, data):
        self.json = data
        self.origin = 'webhook'

    @property
    def actions_path(self):
        return join(
            normpath(abspath(dirname(__file__))),
            '{}_hooks'.format(self.origin)
        )

    @property
    def repo_name(self):
        return ''

    @property
    def branch_name(self):
        return ''

    @property
    def event(self):
        return 'default_event'

    @property
    def actions(self):
        return [] if not isdir(self.actions_path) else [
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

    def get_exe_action(self, action, conf):
        exe_path = join(self.actions_path, action)
        return [exe_path, dumps(self.json), self.event]
