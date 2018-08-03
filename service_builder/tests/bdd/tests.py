# coding=utf-8
"""Drone integration feature tests."""

import os
import shutil

from pytest_bdd import (
    given,
    scenario,
    then,
)

from ...setup_service import _configure_drone_ci
from ...utils import PrettyPrint


@scenario('features/drone_integration.feature',
          'Drone files successfully created')
def test_drone_files_successfully_created():
    name_project = 'test_service'
    os.chdir('..')
    shutil.rmtree(name_project)


@scenario('features/drone_integration.feature',
          'Expected messages for successfully created drone files')
def test_expected_messages_for_successfully_created_drone_files():
    name_project = 'test_service'
    os.chdir('..')
    shutil.rmtree(name_project)


@given('I set up new micro service with drone support')
def i_set_up_new_micro_service_with_drone_support(mocker):
    mocker.spy(PrettyPrint, 'msg_blue')
    name_project = 'test_service'
    shutil.rmtree(name_project, ignore_errors=True)
    os.mkdir(name_project)
    os.chdir(name_project)
    os.mkdir('requirements')
    _configure_drone_ci()


@then('there should be created a file in <file_path> '
      'with <expected_content_filename>')
def there_should_be_created_a_file_in(file_path, expected_content_filename):
    assert os.path.isfile(file_path)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    expected_file_path = os.path.join(current_dir, expected_content_filename)
    with open(expected_file_path, 'r') as expected_file:
        with open(file_path, 'r') as test_file:
            assert expected_file.read() == test_file.read()


@then('<expected_message> should be shown with <expected_color>')
def should_be_shown_with(expected_message, expected_color):
    getattr(PrettyPrint, 'msg_'+expected_color).assert_called_with(
        expected_message)
