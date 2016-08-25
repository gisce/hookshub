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

The test_hooks script implements a test for all the hooks in .../hooks
using a basic request structure by default. You must add the resources and
profile the right test for any new hook inside that script.

This script will be used to test any new pull requests

# Webhooks structure

## Calling structure

```
webhook (base webhook)
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

## Calling requirements

**All webhooks must use at least 2 arguments being:**
```
$ webhook \<data\> \<event\>
```
* Data:   A json string containing all the data(payload) from the hook
* Event:  A string containing the event type
It may also use these arguments:
```
$ webhook [-h] (or --help)   -   will trigger a display showing arguments
$ webhook [-t] (or --test)   -   will trigger the test_actions function for the
                            given data
```


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
