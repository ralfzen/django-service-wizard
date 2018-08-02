import os
import shutil
from unittest import TestCase
from unittest.mock import patch

from django.core.management.base import CommandError

from ..setup_service import setup, _configure_docker, _configure_drone_ci


class SetupTest(TestCase):
    def setUp(self):
        # The script may change directory at times. In case of exception,
        # remember where we are. Otherwise we don't know how to delete folders.
        self.main_dir = os.getcwd()
        self.name_project = 'test_service'
        self.name_application = 'app'
        shutil.rmtree(self.name_project, ignore_errors=True)

    def tearDown(self):
        os.chdir(self.main_dir)
        shutil.rmtree(self.name_project, ignore_errors=True)

    @patch('service_builder.setup_service._configure_docker')
    @patch('service_builder.setup_service._configure_drone_ci')
    @patch('service_builder.setup_service.yes_or_no')
    @patch('service_builder.setup_service.get_input')
    def test_setup_successful(self, mock_get_input, mock_yn,
                              mock_configure_docker, mock_configure_drone_ci):
        mock_get_input.side_effect = [self.name_project, self.name_application]
        mock_yn.return_value = False
        setup()
        self.assertTrue(os.path.isdir(self.name_project))
        self.assertTrue(
            os.path.isdir(
                os.path.join(self.name_project, self.name_application)
            ))
        self.assertTrue(os.path.exists(
            os.path.join(self.name_project, 'requirements', 'base.txt')))
        self.assertFalse(mock_configure_docker.called)
        self.assertFalse(mock_configure_drone_ci.called)

    @patch('service_builder.setup_service._configure_docker')
    @patch('service_builder.setup_service.yes_or_no')
    @patch('service_builder.setup_service.get_input')
    def test_setup_successful_w_docker(self, mock_get_input, mock_yn,
                                       mock_configure_docker):
        mock_get_input.side_effect = [self.name_project, self.name_application]
        mock_yn.return_value = True
        setup()
        self.assertTrue(os.path.isdir(self.name_project))
        self.assertTrue(
            os.path.isdir(
                os.path.join(self.name_project, self.name_application)
            ))
        self.assertTrue(mock_configure_docker.called)

    @patch('service_builder.setup_service.get_input')
    def test_setup_wrong_project_name(self, mock_get_input):
        mock_get_input.side_effect = ['', self.name_application]
        with self.assertRaises(SystemExit) as cm:
            setup()
        self.assertEqual(cm.exception.code, 1)

    @patch('service_builder.setup_service.get_input')
    def test_setup_wrong_app_name(self, mock_get_input):
        mock_get_input.side_effect = [self.name_project, '']
        self.assertRaises(CommandError, setup)


class SetupDockerTest(TestCase):
    def setUp(self):
        self.main_dir = os.getcwd()
        self.name_project = 'test_service'
        shutil.rmtree(self.name_project, ignore_errors=True)

    def tearDown(self):
        os.chdir(self.main_dir)
        shutil.rmtree(self.name_project, ignore_errors=True)

    def test_configure_docker(self):
        os.mkdir(self.name_project)
        os.chdir(self.name_project)
        _configure_docker(self.name_project)

        filename_content_list = (
            ('Dockerfile', 'ENTRYPOINT'),
            ('docker-compose-dev.yml', 'container_name'),
            ('docker-entrypoint.sh',
             'gunicorn -b 0.0.0.0:8080 {}.wsgi'.format(self.name_project)),
        )
        for filename, content_expected in filename_content_list:
            with open(filename, 'r') as file_tpl:
                content = file_tpl.read()
                self.assertIn(content_expected, content)
                self.assertNotIn('{{ name_project }}', content)


class SetupDroneCITest(TestCase):
    def setUp(self):
        self.main_dir = os.getcwd()
        self.name_project = 'test_service'
        shutil.rmtree(self.name_project, ignore_errors=True)

    def tearDown(self):
        os.chdir(self.main_dir)
        shutil.rmtree(self.name_project, ignore_errors=True)

    def test_configure_drone_ci(self):
        os.mkdir(self.name_project)
        os.chdir(self.name_project)
        os.mkdir('requirements')
        _configure_drone_ci()

        filename_content_list = (
            (os.path.join('requirements', 'ci.txt'), 'flake8'),
            ('tcp-port-wait.sh', 'apt install -y netcat'),
            ('.drone.yml', "coverage run --source='.' manage.py test -v 2"),
            ('.flake8', '[flake8]'),
            ('.coveragerc', '*/wsgi.py'),
        )
        for filename, content_expected in filename_content_list:
            with open(filename, 'r') as file_tpl:
                content = file_tpl.read()
                self.assertIn(content_expected, content)
