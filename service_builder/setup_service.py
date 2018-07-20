import os
import shutil

from django.core import management
from django.core.management.base import CommandError

from .utils import (PrettyPrint, replace_text, add_after_variable,
                    append_to_file, get_template_content, get_input)


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
    requirements_dir = os.path.join(name_project, 'requirements')
    shutil.copytree(
        os.path.join('service_builder', 'templates', 'requirements'),
        requirements_dir)

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
    os.chdir(main_dir)
