#
# The objects on this scripts are based on sentry's PluginManager
# Available in :
# - PluginManager: https://github.com/getsentry/sentry/blob/master/src/sentry/plugins/base/manager.py
# - InstanceManager: https://github.com/getsentry/sentry/blob/master/src/sentry/utils/managers.py
#
from collections import namedtuple
from copy import deepcopy
import logging


class InstanceManager(object):
    def __init__(self, class_list=None, instances=True):
        if class_list is None:
            class_list = []
        self.instances = instances
        self.update(class_list)

    def get_class_list(self):
        return self.class_list

    def add(self, class_path):
        self.cache = None
        self.class_list.append(class_path)

    def exists(self, class_path):
        return class_path in list(self.get_class_list())

    def get(self, class_path):
        if not self.exists(class_path):
            return None
        module_name, class_name = class_path.rsplit('.', 1)
        try:
            module = __import__(module_name, {}, {}, class_name)
            cls = getattr(module, class_name)
            if self.instances:
                return cls()
            else:
                return cls
        except Exception:
            logger = logging.getLogger('hookshub.errors')
            logger.exception('Unable to import %s', class_path)
            return None

    def remove(self, class_path):
        self.cache = None
        self.class_list.remove(class_path)

    def update(self, class_list):
        """
        Updates the class list and wipes the cache.
        """
        self.cache = None
        self.class_list = class_list

    def all(self):
        """
        Returns a list of cached instances.
        """
        class_list = list(self.get_class_list())
        if not class_list:
            self.cache = []
            return []

        if self.cache is not None:
            return self.cache

        results = []
        for cls_path in class_list:
            module_name, class_name = cls_path.rsplit('.', 1)
            try:
                module = __import__(module_name, {}, {}, class_name)
                cls = getattr(module, class_name)
                if self.instances:
                    results.append(cls())
                else:
                    results.append(cls)
            except Exception:
                logger = logging.getLogger('hookshub.errors')
                logger.exception('Unable to import %s', cls_path)
                continue
        self.cache = results

        return results


class PluginManager(InstanceManager):

    def __init__(self):
        super(PluginManager, self).__init__()
        self._hooks_list = []

    def __iter__(self):
        return iter(self.all())

    def __len__(self):
        return sum(1 for i in self.all())

    def all(self, version=1):
        for plugin in sorted(
                super(PluginManager, self).all(),
                key=lambda x: x.title
        ):
            if not plugin.enabled:
                continue
            if version is not None and plugin.__version__ != version:
                continue
            yield plugin

    def get_hooks(self):
        return deepcopy(self._hooks_list)

    def register(self, cls):
        cls_name = '%s.%s' % (cls.__module__, cls.__name__)
        if self.exists(cls_name):
            self.remove(cls_name)
        self.add(cls_name)
        inst = self.get(cls_name)
        hook_name = cls_name.replace('.', '_')
        hook_data = namedtuple(
            hook_name,
            'hook, event, repository, branch'
        )
        hook_data.hook = inst.hook
        hook_data.event = inst.event
        hook_data.repository = inst.repository
        hook_data.branch = inst.branch
        self._hooks_list.append(hook_data)
        return cls

    def unregister(self, cls):
        cls_name = '%s.%s' % (cls.__module__, cls.__name__)
        hook_name = cls_name.replace('.', '_')
        if not self.exists(cls_name):
            return False
        hook_data = namedtuple(
            hook_name,
            'hook, event, repository, branch'
        )
        inst = self.get(cls_name)
        hook_data.hook = inst.hook
        hook_data.event = inst.event
        hook_data.repository = inst.repository
        hook_data.branch = inst.branch
        self._hooks_list.remove(hook_data)
        self.remove(cls_name)
        return cls

plugins = PluginManager()
hooks = plugins.get_hooks()
