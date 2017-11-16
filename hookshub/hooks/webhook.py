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
        return 'default_repository'

    @property
    def branch_name(self):
        return 'default_branch'

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
        """
        Find for the scripts in the hook's directory:
            hookshub/hooks/webhook_hooks
        For all actions (scripts) that are named after:
            <event>-<repository>-<branch>
            <event>-<repository>_<comment>
            <event>-<repository>
            <event>_<comment>
            <event>
        :return: All the scripts that match with the event decoded
        :rtype: List<String>
        """
        events = [] if not isdir(self.actions_path) else [
            action
            for action in listdir(self.actions_path)
            if (
                action.startswith(self.event) and
                isfile(join(self.actions_path, action))
            )
        ]
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
            event == '{0}-{1}.py'.format(self.event, self.repo_name) or
            # If they start with {event}_{name}
            event.startswith('{0}_'.format(self.event)) or
            # If they are named after {event}
            event == '{0}.py'.format(self.event)
        ]
        return events

    def get_exe_action(self, action, conf):
        exe_path = join(self.actions_path, action)
        return [exe_path, dumps(self.json), self.event]
