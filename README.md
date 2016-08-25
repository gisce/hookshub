# github-hooks
Our hooks for github

## Permissions
The hooks and actions MUST be executables by another program
```
$ chmod 711 hook_name
```
## Coding
The actions may use any coding language as long as the machine can
execute them individually

The webhooks must be implemented in python as they extend the base webhook
implemented in python

## Testing
All the actions can and will be tested from the parent webhook

**This script will be used to test any new pull requests**

The test_hooks script implements a test for all the hooks in .../hooks

This script:
* Tries to execute each hook in the hooks directory (../project/hooks)
* Calls each hook with each of the test_data events
  * For each hook, there must be a test_data for each event that the
    hook may need located in the testing data directory 
    (..project/test_data/{webhook}/)
  * The hooks themselves include a function (extended from base
    webhook) that executes each action for the current event
* If any of the actions fails with the given arguments, the hook test fails.
* If any of the hook test fails or cannot be started, the test_hooks fails.

**!!! TODO : Testing action may not execute them the same way as a functional hook may trigger !!!**

# Webhooks structure

## Calling structure

```
hook_parse (checks JSON to find the origin, then instances a webhook)
|------> webhook (base webhook)
|         |----------> default_action
|------> github_hook (webhook instance; extends webhook; executable)
|         |----------> [action/hook](#requirements-for-the-hooks-actions)
|         |----------> action/hook (for an event of the hook type request)
|         |----------> ...
|------> gitlab_hook
|------> ...
```

## Directory structure

Base webhook location   
...project/webhook.py

Other webhooks location   
..project/hooks/{webhook}

Actions location   
..project/hooks/{webhook}/{action}

Test data location   
..project/test_data/{webhook}/{event}

## Calling requirements

**All webhooks must use at least 2 arguments being:**

```
$ webhook [-h|--help] \<data\> \<event\> [-t|--test]
```

* Data:   A string containing a file with json data from the request
* Event:  A string containing the event type
* [-h or --help]   -   will trigger a display showing arguments
* [-t or --test]   -   will trigger the test_actions function for the
                            given data

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
