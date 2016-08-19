# github-hooks
Our hooks for github

## Requirements for the hooks
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

### Permissions
The hooks MUST be executables by another program
```
$ chmod 711 hook_name
```
### Coding
The hooks may use any coding language as long as the machine can execute them individually
