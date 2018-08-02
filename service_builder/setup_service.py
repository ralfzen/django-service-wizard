import os

from django.core import management
from django.core.management.base import CommandError

from .utils import (PrettyPrint, replace_text, add_after_variable,
                    append_to_file, get_template_content, get_input, yes_or_no)


def _welcome_msg():
    PrettyPrint.msg_blue('Welcome to Humanitec MicroService wizard!')
    PrettyPrint.print_green("                  .' '.            __")
    PrettyPrint.print_green("         .        .   .           (__\_")
    PrettyPrint.print_green("          .         .         . -{{_(|8)")
    PrettyPrint.print_green("            ' .  . ' ' .  . '     (__/\`\n")
    PrettyPrint.msg_blue('We will help you to set up a MicroService :)')


def _create_project(name: str):
    management.ManagementUtility(
        ['manage.py', 'startproject', name]).execute()
    PrettyPrint.msg_blue(
        'The Django project "{}" was successfully created'.format(name))


def _configure_project(name_project: str):
    # Add requirements
    os.mkdir(os.path.join(name_project, 'requirements'))
    file_requirements = os.path.join('requirements', 'base.txt')
    content = get_template_content(file_requirements)
    open(os.path.join(name_project, file_requirements), 'a').close()
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

    # Modify manage.py default Django settings
    file_manage_py = os.path.join(name_project, 'manage.py')
    replace_text(file_manage_py,
                 '{}.settings'.format(name_project),
                 '{}.settings.base'.format(name_project))

    # Add README
    file_readme = os.path.join(name_project, 'README.md')
    open(os.path.join(file_readme), 'a').close()
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


def _configure_docker(name_project):
    filenames = ('Dockerfile', 'docker-compose-dev.yml',
                 'docker-entrypoint.sh')
    for filename in filenames:
        content = get_template_content(os.path.join('docker', filename))
        content = content.replace('{{ name_project }}', name_project)
        append_to_file(filename, content)

    # Add README info
    file_readme = 'README.md'
    content = get_template_content(os.path.join('readme', 'docker.md'))
    append_to_file(file_readme, content)

    PrettyPrint.msg_blue('Docker support was successfully added')


def _configure_drone_ci():
    file_requirements = os.path.join('requirements', 'ci.txt')
    content = get_template_content(file_requirements)
    open(file_requirements, 'a').close()
    append_to_file(file_requirements, content)

    file_flake8 = '.flake8'
    content = get_template_content(os.path.join('drone-ci', file_flake8))
    open(file_flake8, 'a').close()
    append_to_file(file_flake8, content)

    file_coverage = '.coveragerc'
    content = get_template_content(os.path.join('drone-ci', file_coverage))
    open(file_coverage, 'a').close()
    append_to_file(file_coverage, content)

    file_drone = '.drone.yml'
    content = get_template_content(os.path.join('drone-ci', file_drone))
    open(file_drone, 'a').close()
    append_to_file(file_drone, content)

    file_tcp = 'tcp-port-wait.sh'
    content = get_template_content(os.path.join('drone-ci', file_tcp))
    open(file_tcp, 'a').close()
    append_to_file(file_tcp, content)
    os.chmod(file_tcp, 0o755)

    PrettyPrint.msg_blue('Drone CI support was successfully added. Make sure '
                         'to configure the needed permissions in the Drone CI '
                         'web administration panel')


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

    is_answer_yes = yes_or_no('Add Docker support?')
    if is_answer_yes:
        _configure_docker(name_project)

    is_answer_yes = yes_or_no(
        'Add Drone CI test support?')
    if is_answer_yes:
        _configure_drone_ci()

    os.chdir(main_dir)
