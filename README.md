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
* Our [Python HTTP Listener](https://github.com/gisce/python-github-webhooks)
  * [Original HTTP Listener](https://github.com/carlos-jenkins/python-github-webhooks)(only for github, does not work with this repository but may work with our GitHub actions)
* [Mamba Testing](https://github.com/nestorsalceda/mamba)
* [JSON Example](http://json.org/example.html)

## Configuration

In order to work properly some environment variables may be declared. That way the tokens won't be pushed by mistake and that kind of sensible data may only be visible by the developer.

The required variables are:
```
$vhost_path   - Contains the path to the virtualhost (target path to build)
$github_token - Your github_token required to OAuth with GitHub
$gitlab_token - Your github_token required to OAuth with GitLab
```

A defaults file for the environment variables is required in order to instanciate the `listener` class.
This file may be readed as a JSON Document with the variables names as key names.

Doing so, if there's no environment variable, the data in the defaults file will be used.

If those variables are not found in any of the two resources, the listener may raise an exception.

As probably you'll be using our [Python HTTP Listener](https://github.com/gisce/python-github-webhooks) you may want to create this file in its folder as it may be looking for it (check its readme)

## Tokens

As instanced in its documentation, Tokens are used by requests to skip the authentication process.

It's important that the tokens used are created properly by an account with permissions over the repositories that the actions work on.

Check the documentation about Tokens referenced on [GitHub and OAuth](https://developer.github.com/v3/oauth/) and the [GitLab API](https://docs.gitlab.com/ce/api/). This may also work with other pages that have implemented the OAuth System.

## Elements: Listener, Hooks and Actions

This repo is based on 3 types as you may expect, they are the Listener, the Hooks and the Actions.

The Listener is created by our [Python HTTP Listener](https://github.com/gisce/python-github-webhooks) and it does instanciate a Hook depending on the payload that it gets. With its `run_event_actions` method and a path for a default configuration file, the listener may instanciate a Hook and run all the actions required acording to the event and the payload recieved. When it ends, it may return a code, saying if it went all ok (`0`) or if something went wrong (`-1`) and a log string, containing the log with output and errors of the actions and/or the hook.

On the other hand, the Hooks are created just with the payload and contain all info about a Hook from it's origin. The listener may instanciate each of them according to its origin, but they have the same methods and properties adapted to each of the hooks.

Finally the actions are the most important elements on this repository. They run actions according to a hook's event and settings. Each Hook may instanciate it's own call to an action, but by default our actions may need a payload argument with JSON style. The actions themselves may be executed individually with the correct input (argument) so, they must be executable.

## Testing

We use [MAMBA](https://github.com/nestorsalceda/mamba) for testing. If you may want to run or update the tests, remember that they may be located in the `/spec/` directory and you may be able to execute them with the following commands:
```
$mamba
$mamba --format=documentation
```

## File Structure
