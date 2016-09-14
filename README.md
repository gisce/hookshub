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

## Elements: Listener, Hooks and Actions

## Testing

## File Structure
