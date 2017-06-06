from os.path import join, isdir
import os


def pip_requirements(dir):
    """
    Installs all the requirements from the requirements.txt in the specified
    directory. If no virtualenv is set previously for the Popen, they will
    be installed in the user's python directory
    :param dir: Directory where the requirements.txt is found. Used to call
        Popen with the pip install.
        :type: String
    :return: Output with the log. Does not include any of the pip install
        output or error prints.
    :rtype: String
    """
    output = 'Instal.lant dependencies...'
    command = 'pip install -r {}'.format(join(dir, 'requirements.txt'))
    log_file = join(dir, "pip.log")
    command += " > {0} 2> {0}".format(log_file)
    dependencies = os.system(command)
    with open(log_file, 'r') as stout:
        out = stout.read()
    os.system('rm {}'.format(log_file))
    if dependencies != 0:
        output += ' Couldn\'t install all dependencies!\n{}'.format(
            out
        )
    else:
        output += " OK"
    return output


def export_pythonpath(docs_path):
    """
    :param docs_path: Path to the docs clone. Must have the sitecustomize
        directory, as that's what the $PYTHONPATH will point to
        :type:  String
    :return: An output log saying if everything was ok
    """
    sc_path = join(docs_path, 'sitecustomize')
    command = 'export PYTHONPATH={}'.format(sc_path)
    export = os.system(command)
    if export:
        return 'Failed to export sitecustomize path'
    return 'Success to export sitecustomize path'


def create_virtualenv(name='foo', dir='/tmp/venv'):
    if not isdir(dir):
        os.system('mkdir -p {}'.format(dir))
    dest = join(dir, name)
    log = '{}.log'.format(name)
    logs = join(dir, log)
    os.system('virtualenv {0} > {1} 2> {1}'.format(dest, logs))
    activate = join(dest, 'bin', 'activate_this.py')
    execfile(activate, dict(__file__=activate))
    return dest


def mkdocs_build(dir, target=None, file=None, clean=True):
    """
    :param dir: Directory used to call the build. This MUST exist.
        :type:  String
    :param file: Configuration file used to build with. If None is set,
        the '-f' option is not used, using the default 'mkdocs.yml' config
        :type:  String
    :param target: Directory to build to. If not set or None, the target
        build is the default one, that is the same as 'dir'
        :type:  String
    :param clean: Defines if the '--clean' tag is used or not. If true,
        this cleans the directory before the build.
        :type:  Bool
    :return: The command to all with the specified params, thus not all
        environments support processes (or are not desired)
    """
    build_path = dir
    output = 'Building mkdocs from {} '.format(dir)
    command = 'cd {} && mkdocs build'.format(dir)
    if target:
        build_path = target
        output += 'to {}...'.format(target)
        command += ' -d {}'.format(target)
    if file:
        output += ' using file config file "{}"...'.format(file)
        command += ' -f {}'.format(file)
    if clean:
        command += ' --clean'
    log_file = join(dir, 'build.log')
    command += " > {0} 2> {0}".format(log_file)
    new_build = os.system(command)
    with open(log_file, 'r') as stout:
        out = stout.read()
    os.system('rm {}'.format(log_file))
    if new_build != 0:
        output += 'FAILED TO BUILD: {}'.format(out)
        return output, False
    output += " OK"
    return output, build_path


def lektor_build(dir, target=None, project=None):
    """
    :param dir: Directory used to call the build. This MUST exist.
        :type:  String
    :param target: Directory to build to. If not set or None, the target
        build is the default one, that is the same as 'dir'
        :type:  String
    :param project: Project to find in the directory, used by lektor command
        May be None, and is not used if in the right directory.
        :type:  String
    :return: An output log with some annotations and the output and error
        log from the lektor build call. And a String containing the path
        where the docs have been built
        :type: Tuple<String, String>
    """
    build_path = dir
    output = 'Building lector from {} '.format(dir)
    command = 'lektor'
    if project:
        output += 'for the project {} '.format(project)
        command += ' --project {}'.format(project)
    command += ' build'
    if target:
        build_path = target
        output += 'to {}...'.format(target)
        command += ' -O {}'.format(target)
    log_file = join(dir, 'build.log')
    command += " > {0} 2> {0}".format(log_file)
    new_build = os.system(command)
    with open(log_file, 'r') as stout:
        out = stout.read()
    os.system('rm {}'.format(log_file))
    if new_build != 0:
        output += 'FAILED TO BUILD: {}'.format(out)
        return output, False
    output += " OK"
    return output, build_path