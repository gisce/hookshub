from pkg_resources import iter_entry_points
import logging


class Hook(object):
    def __init__(self, method, event=False, repository=False, branch=False):
        self._name = str(self.__class__)
        self._hook = method
        self._event = event
        self._repository = repository
        self._branch = branch
        self._enabled = False

    def is_enabled(self):
        return self._enabled

    def enable(self):
        self._enabled = True
        return self.is_enabled()

    def disable(self):
        self._enabled = False
        return self.is_enabled()

    @property
    def title(self):
        return self._name

    @property
    def hook(self):
        return self._hook

    @property
    def event(self):
        return self._event

    @property
    def repository(self):
        return self._repository

    @property
    def branch(self):
        return self._branch

    @property
    def enabled(self):
        return self._enabled


def get_hooks(event=False, repository=False, branch=False):
    from hookshub.plugins import hooks
    results = []
    for hook, ev, repo, br in hooks:
        if event:
            event = ev == event
        if repository:
            repository = repo == repository
        if branch:
            branch = br == branch
        if event and repository and branch:
            results.append(hook)
    return results


def reload_hooks():
    from hookshub.plugins import plugins
    logger = logging.getLogger()
    for entrypoint in iter_entry_points('hookshub.plugins'):
        try:
            plugin = entrypoint.load()
        except Exception as e:
            logger.error('Could not load plugin {}:\n{}'.format(
                entrypoint, e
            ))
        else:
            plugins.register(plugin)
