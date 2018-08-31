import os

from django.core import management
from django.core.management.base import CommandError

from .utils import (PrettyPrint, replace_text, add_after_variable,
                    append_to_file, get_template_content, get_input, yes_or_no)


def _welcome_msg():
    PrettyPrint.msg_blue('Welcome to Humanitec MicroService wizard!')
    PrettyPrint.print_green("""
  /\  /\_   _ _ __ ___   __ _ _ __ (_) |_ ___  ___
 / /_/ / | | | '_ ` _ \ / _` | '_ \| | __/ _ \/ __|
/ __  /| |_| | | | | | | (_| | | | | | ||  __/ (__
\/ /_/  \__,_|_| |_| |_|\__,_|_| |_|_|\__\___|\___|

    """)
    PrettyPrint.msg_blue('We will help you to set up a MicroService :)')


def _create_project(name: str):
    management.ManagementUtility(
        ['manage.py', 'startproject', name]).execute()
    PrettyPrint.msg_blue(
        'The Django project "{}" was successfully created'.format(name))


def _configure_project(name_project: str):
    # Add .gitignore
    content = get_template_content(os.path.join('gitignore', '.gitignore'))
    append_to_file(os.path.join(name_project, '.gitignore'), content)

    # Add requirements
    os.mkdir(os.path.join(name_project, 'requirements'))
    files_requirements = (
        os.path.join('requirements', 'base.txt'),
        os.path.join('requirements', 'production.txt'),
    )
    for file_requirements in files_requirements:
        content = get_template_content(file_requirements)
        append_to_file(os.path.join(name_project, file_requirements), content)

    # Create settings python module
    settings_dir = os.path.join(name_project, name_project, 'settings')
    os.mkdir(settings_dir)
    open(os.path.join(settings_dir, '__init__.py'), 'a').close()

    file_settings = os.path.join(settings_dir, 'base.py')
    os.rename(
        os.path.join(name_project, name_project, 'settings.py'),
        file_settings,
    )

    file_settings_production = os.path.join(settings_dir, 'production.py')
    open(file_settings_production, 'a').close()

    # Configure settings
    replace_text(file_settings,
                 'DEBUG = True',
                 "DEBUG = False if os.getenv('DEBUG') == 'False' else True")
    replace_text(file_settings, 'INSTALLED_APPS', 'INSTALLED_APPS_DJANGO')

    content = get_template_content(os.path.join('settings',
                                                'base_installedapps.tpl'))
    add_after_variable(file_settings, 'INSTALLED_APPS_DJANGO', content)

    content = get_template_content(os.path.join('settings',
                                                'base_appended.tpl'))
    append_to_file(file_settings, content)

    content = get_template_content(os.path.join('settings', 'production.tpl'))
    append_to_file(file_settings_production, content)

    # Configure databases
    replace_text(
        file_settings,
        "'ENGINE': 'django.db.backends.sqlite3'",
        "'ENGINE': 'django.db.backends.{}'.format(os.environ['DATABASE_ENGINE'])"  # noqa
    )
    replace_text(
        file_settings,
        "        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),",
        """\
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.environ['DATABASE_PORT'],\
        """)

    # Modify wsgi.py
    file_wsgi = os.path.join(name_project, name_project, 'wsgi.py')
    replace_text(file_wsgi,
                 '{}.settings'.format(name_project),
                 '{}.settings.production'.format(name_project))

    # Modify manage.py default Django settings
    file_manage_py = os.path.join(name_project, 'manage.py')
    replace_text(file_manage_py,
                 '{}.settings'.format(name_project),
                 '{}.settings.base'.format(name_project))

    # Add README
    file_readme = os.path.join(name_project, 'README.md')
    content = get_template_content(os.path.join('readme', 'README.md'))
    content = content.replace('{{ name_project }}', name_project)
    append_to_file(file_readme, content)


def _create_app(name_project: str, name_app: str):
    main_dir = os.getcwd()
    os.chdir(name_project)
    try:
        management.call_command('startapp', name_app)
    except CommandError:
        os.chdir(main_dir)
        raise
    else:
        PrettyPrint.msg_blue(
            'The app "{}" was successfully created'.format(name_app))

    # Add new app to settings
    file_settings = os.path.join(name_project, 'settings', 'base.py')
    replace_text(file_settings, '{{ name_app }}', name_app)


def _configure_docker(name_project: str):
    filenames = (
        os.path.join('docker', 'Dockerfile'),
        os.path.join('docker', 'docker-compose-dev.yml'),
        os.path.join('docker', 'docker-entrypoint.sh'),
        os.path.join('docker', 'run-standalone-dev.sh'),
        os.path.join('utils', 'tcp-port-wait.sh'),
    )
    for filename in filenames:
        content = get_template_content(filename)
        content = content.replace('{{ name_project }}', name_project)
        append_to_file(os.path.basename(filename), content, recreate=True)

    # Add README info
    file_readme = 'README.md'
    content = get_template_content(os.path.join('readme', 'docker.md'))
    append_to_file(file_readme, content)

    PrettyPrint.msg_blue('Docker support was successfully added')


def _configure_drone_ci():
    files_to_copy = [
        {
            'source': os.path.join('requirements', 'ci.txt'),
            'destination': os.path.join('requirements', 'ci.txt')
        },
        {
            'source': os.path.join('drone-ci', '.flake8'),
            'destination': os.path.join('.flake8')
        },
        {
            'source': os.path.join('drone-ci', '.coveragerc'),
            'destination': os.path.join('.coveragerc')
        },
        {
            'source': os.path.join('drone-ci', '.drone.yml'),
            'destination': os.path.join('.drone.yml')
        },
        {
            'source': os.path.join('utils', 'tcp-port-wait.sh'),
            'destination': os.path.join('tcp-port-wait.sh')
        },
    ]

    for file in files_to_copy:
        append_to_file(
            filename=file['destination'],
            text_to_append=get_template_content(file['source']),
            recreate=True,
        )

    PrettyPrint.msg_blue('Drone CI support was successfully added. Make sure '
                         'to configure the needed permissions in the Drone CI '
                         'web administration panel')


def _configure_docker_registry(name_project: str, registry_domain: str,
                               registry_folder: str):
    registry_url = os.path.join(registry_domain, registry_folder, name_project)
    filename = os.path.join('drone-ci', '.drone-appendix.yml')
    content = get_template_content(filename)
    content = content.replace('{{ registry_domain }}', registry_domain)
    content = content.replace('{{ registry_url }}', registry_url)
    append_to_file(filename='.drone.yml', text_to_append=content)


def setup():
    main_dir = os.getcwd()
    _welcome_msg()
    name_project = get_input(
        'Type in the name of your service (e.g.: appointments_service):')
    _create_project(name_project)
    _configure_project(name_project)
    name_app = get_input(
        'Type in the name of your application (e.g.: appointment):')
    _create_app(name_project, name_app)

    is_answer_yes_docker = yes_or_no('Add Docker support?')
    if is_answer_yes_docker:
        _configure_docker(name_project)

    is_answer_yes_drone = yes_or_no('Add Drone CI test support?')
    if is_answer_yes_drone:
        _configure_drone_ci()

    if is_answer_yes_docker and is_answer_yes_drone:
        is_answer_yes = yes_or_no(
            'Add Docker registry support to Drone?')
        if is_answer_yes:
            registry_domain = get_input(
                'Type in the domain of the registry (e.g.: registry.tola.io):')
            registry_folder = get_input(
                'Type the folder of the registry (e.g.: toladata):')
            _configure_docker_registry(name_project, registry_domain,
                                       registry_folder)

    PrettyPrint.msg_blue(
        'Great! Now you can find your new project inside the current\'s '
        'wizard folder with name "{}"'.format(name_project))
    os.chdir(main_dir)
