# HooksHub
Our Hub of Hooks

[![Build Status](https://travis-ci.org/gisce/hookshub.svg?branch=master)](https://travis-ci.org/gisce/hookshub)
[![Coverage Status](https://coveralls.io/repos/github/gisce/github-hooks/badge.svg?branch=master)](https://coveralls.io/github/gisce/github-hooks?branch=master)

### Contents

 * [Installation](#installation)
 * [References](#references)
 * [Configuration](#configuration)
 * [Tokens](#tokens)
 * [Elements](#elements-listener-hooks-and-actions)
 * [Tests](#testing)
 * [File Structure](#file-structure)
 * [Add your own hooks](#adding-hooks)


## Installation

There's no official release (yet?), but there's a setup.py, so you can install this project with pip or easy-install.   
Use the `pip install .` command within the project folder.   
On requirements.txt you may need the whole git url.   

There are a few configurations in order to work properly. Check the [configuration section](#configuration) to get more information.

## References

* [Github hooks](https://developer.github.com/v3/activity/events/types/)
* [Gitlab hooks](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/doc/web_hooks/web_hooks.md)
* GitHub Tokens
  * [How to create a github token](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
  * [GitHub and OAuth](https://developer.github.com/v3/oauth/)
* [GitLab API](https://docs.gitlab.com/ce/api/)
* [Flask Docs](http://flask.pocoo.org/docs/0.12/)
* [Mamba Testing](https://github.com/nestorsalceda/mamba)
* [JSON Example](http://json.org/example.html)
* [Entry Points](http://setuptools.readthedocs.io/en/latest/pkg_resources.html)

## Configuration

In order to work properly some environment variables may be declared. That way the tokens won't be pushed by mistake and that kind of sensible data may only be visible by the developer.

The required variables are:
```
$VHOST_PATH     - Contains the path to the virtualhost (target path to build)
$GITHUB_TOKEN   - Your github_token required to OAuth with GitHub
$GITLAB_TOKEN   - Your github_token required to OAuth with GitLab
$ACTION_TIMEOUT - Timeout for the spawned processes. They'll keep running but async
```

### Listener Server

When running the listener server, you can use some parameters to improve the usability.

Usage can be described using the `--help` parameter, and it shows:

```
python listener.py [options]

    [--ip=<ip_address>]         -   @IP address to bind and listen to hooks
    [--port=<port_number>]      -   Port number to bind and listen to hooks
    [--procs=<process_number>]  -   Process number to spawn to run actions
```

----

A defaults file for the environment variables is required in order to instanciate the `listener` class.
This file may be readed as a JSON Document with the variables names as key names.

Doing so, if there's no environment variable, the data in the defaults file will be used.

If those variables are not found in any of the two resources, the listener may raise an exception.

The configuration file is loaded in the path _{cwd}/config.json_

## Tokens

As instanced in its documentation, Tokens are used by requests to skip the authentication process.

It's important that the tokens used are created properly by an account with permissions over the repositories that the actions work on.

Check the documentation about Tokens referenced on [GitHub and OAuth](https://developer.github.com/v3/oauth/) and the [GitLab API](https://docs.gitlab.com/ce/api/). This may also work with other pages that have implemented the OAuth System.

## Elements: Listener, Hooks and Actions

This repo is based on 3 types as you may expect, they are the Listener, the Hooks and the Actions.

The Listener is created by our [Python HTTP Listener](https://github.com/gisce/python-github-webhooks) and it does instanciate a Hook depending on the payload that it gets. With its `run_event_actions` method and a path for a default configuration file, the listener may instanciate a Hook and run all the actions required acording to the event and the payload recieved. When it ends, it may return a code, saying if it went all ok (`0`) or if something went wrong (`-1`) and a log string, containing the log with output and errors of the actions and/or the hook.

On the other hand, the Hooks are created just with the payload and contain all info about a Hook from it's origin. The listener may instanciate each of them according to its origin, but they have the same methods and properties adapted to each of the hooks.

Finally the actions are the most important elements on this repository. They run actions according to a hook's event and settings. Each Hook may instanciate it's own call to an action, but by default our actions may need a payload argument with JSON style. The actions themselves may be executed individually with the correct input (argument) so, they must be executable.

### Action Naming

*All actions may instance the following structure, and will only work if the event, repository and branch names are found*:
* **event_** _name_
* **event.py**
* **event-repository_** _name_
* **event-repository.py**
* **event-repository-branch_** _name_
* **event-repository-branch.py**

## Testing

We use [MAMBA](https://github.com/nestorsalceda/mamba) for testing. If you may want to run or update the tests, remember that they may be located in the `/spec/` directory and you may be able to execute them with the following commands:
```
$mamba
$mamba --format=documentation
```

The tests may use fake but correct data. Located in the `test_data` directory.

## File Structure

All the Elements are located inside the `/hookshub/` directory ready to be installed.
* The Actions are located inside a folder with its parent hook's name (a github action may be in `/github/`).
* The Hooks are inside the `/hooks/` directory.
* The Listener is inside the HooksHub main directory.

The tests are located in the `/spec/` directory.

The test data is located in the `/test_data/` directory

## Adding Hooks

You can add your own hooks actions in two ways:

1. Adding actions in the hook actions folder (hookshub/hooks/<origin>-hooks/executable)
2. **Implement your own hook with entry points**

The listener process may update the hooks installed so hotfixes are on!

You just need to implement your own Python package with a setup and install it!

Remember to add the entry point in the setup.

Example setup.py with entry_point:

```python
setup(
    name='nice-hooks',
    version='0.1.0',
    author='Jaume Florez',
    author_email='jflorez@gisce.net',
    url='https://gitlab.com/jaumef/nice-hooks', # Does not exist ;)
    description='A HooksHub extension with nice hooks',
    long_description=__doc__,
    license='GNUv3',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'hookshub.plugins': [
            'foohook = nice-hooks.hook:FooVarHook'
        ],
    },
    include_package_data=True,
)
```

Where there is a file located in `/<nice-hooks-repository>/nice-hooks/hook.py`
that contains the hook:

```python
def nice_method(args):
  print('Doing nice things')


class FooVarHook(Hook):
    def __init__(self):
        super(FooVarHook, self).__init__(
            method=nice_method,   # Method to run by the hook
            event=False,          # Event where the hook will trigger
            # (you can import it from HooksHub webhooks.events)
            repository=False,     # Repository where the hook will trigger
            branch=False          # Branch where the hook will trigger
        )

    def get_args(self, webhook=False, conf=False):
        # Define your own get_args method given a webhook payload and
        # an environment conf.
        # Returns full webhook payload by default
        dict = {}
        if conf:
            dict.update({
                'conf': True
            })
        if webhook:
            dict.update({
                'webhook': True
            })
        if not dict:
            dict = {
                'Default': True
            }
        return dict
```
