# github-hooks
Our hooks for github

## References

* [Github hooks](https://developer.github.com/v3/activity/events/types/)
* [Gitlab hooks](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/doc/web_hooks/web_hooks.md)

## Permissions
* Listener must be executable
* Webhooks must be readable
* Actions must be executables
* Test data must be readable
```
$ chmod 711 action-name // listener
$ chmod 622 webhooks // test-data
```
## Coding
The actions may use any coding language as long as the machine can
execute them individually

The webhooks must be implemented in python as they extend the base webhook
implemented in python

Test data is written under JSON string and it simulates the data of a request

## Testing

All the actions can and will be tested from the parent webhook

The test_hooks script will use the resources on /test_data/{hook} to test for
each hook in /hooks/.

The test data are simulated inputs for the events handled by the hook. There
must be a test data for each event of the hook that is being used as an action
in /hooks/{hook}/.

The test data files must be named after the events they simulate, the same way
the actions are named.

**This script will be used to test any new pull requests on the hooks repository**

## Adding Files

All the files you may add MUST:

- Have been located properly (check the [directory structure](#directory-structure))
- Have a test
- Have been documented **TODO**

### Add a new action for a hook

* Test data must simulate the hook's request data
* The hook action MUST NOT instanciate a case for test which skips the code
  * But it CAN work on a temporal directory if there are changes on the disk

### Add a new hook

* There MUST be a basic JSON origin patron implemented at test_hooks.origin
* There MUST be a test for each action performed by the hook

## Calling structure

```
listener (webhook dispatcher; executable)
|------> webhook (base webhook)
|--------------------> default_event (event from webhook; executable)
|------> github_hook (webhook instance; extends webhook)
|--------------------> event (event from github_hook)
|------> gitlab_hook
|------> ...
```

## Directory structure

Base listener location
...project/listener.py

Test location
...project/test_hooks.py

Test Data location
...project/test_data/{webhook}/{action}

Webhooks location
..project/hooks/{webhook}

Actions location
..project/hooks/{webhook}/{action}

## Requirements for the hooks actions

### Naming
**The names of the hooks are important!**
The names MUST NOT HAVE ANY EXTENSION
The names MUST be named after:
* {event}-{repository_name}-{branch_name}
  * For the event and the repository and the branch selected
* {event}-{repository_name}
  * For the event and the repository selected on any branch
* {event}
  * For the event selected, on any repository and any branch
* all
  * On any event and any repository and any branch

## Calling requirements

There are 2 relevant scripts that must be documented here:

1. listener.py
2. test_hooks.py

```
$ listener.py [-t|--test] (payload) ([-t|--test] | event)
```
* [-t|--test]
  - As a first argument, this will instanciate a 'webhook' with a default
    payload and execute a test for it. ONLY IN THIS CASE YOU CAN SKIP THE
    OTHER ARGUMENTS.
  - As a second argument, this will trigger the test for each action in
    /test_data/{hook} for the hook instanciated with the payload
* (payload)
  - It's the name of the file that contains a JSON Document. This may be either
    permanent or temporal as long as it can be readed once.
  - It's used to do both find the origin of the request and process it
* (event)
  - It's not a required element, as it can be (and is) obtained from the payload
  - It's use is for testing the payload parse as long as they are in the call

```
$ test_hooks.py
```

Just use it as a script, this will trigger the listener for each hook origin it
has initialized.
