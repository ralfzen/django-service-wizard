import os
import shutil
from unittest import TestCase
from unittest.mock import patch

from django.core.management.base import CommandError

from ..setup_service import (
    setup, _configure_docker, _configure_docker_registry)


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

    @patch('service_builder.setup_service.PrettyPrint')
    @patch('service_builder.setup_service._configure_docker')
    @patch('service_builder.setup_service._configure_drone_ci')
    @patch('service_builder.setup_service._configure_docker_registry')
    @patch('service_builder.setup_service.yes_or_no')
    @patch('service_builder.setup_service.get_input')
    def test_setup_successful(self, mock_get_input, mock_yn,
                              mock_configure_docker_registry,
                              mock_configure_drone_ci, mock_configure_docker,
                              mock_prettyprint):
        mock_get_input.side_effect = [self.name_project, self.name_application]
        mock_yn.return_value = False
        setup()

        # Check project and app are there
        self.assertTrue(os.path.isdir(self.name_project))
        self.assertTrue(
            os.path.isdir(
                os.path.join(self.name_project, self.name_application)
            ))

        # Gitignore
        file_gitignore = os.path.join(self.name_project, '.gitignore')
        self.assertTrue(os.path.exists(file_gitignore))
        with open(file_gitignore, 'r') as fp:
            content = fp.read()
        self.assertEqual(content, """\
*.pyc
""")

        # wsgi.py
        file_wsgi = os.path.join(self.name_project, self.name_project,
                                 'wsgi.py')
        with open(file_wsgi, 'r') as file_tpl:
            content = file_tpl.read()
            self.assertIn(
                '{}.settings.production'.format(self.name_project),
                content)

        # Requirements
        file_base = os.path.join(self.name_project, 'requirements', 'base.txt')
        self.assertTrue(os.path.exists(file_base))
        with open(file_base, 'r') as fp:
            content = fp.read()
        self.assertEqual(content, """\
Django==2.0.9
django-filter==2.0.0
django-health-check==3.6.1
git+https://github.com/Humanitec/django-oauth-toolkit-jwt@v0.4.0#egg=django-oauth-toolkit-jwt
djangorestframework==3.8.2
psycopg2-binary==2.7.5
""")
        file_production = os.path.join(self.name_project, 'requirements',
                                       'production.txt')
        self.assertTrue(os.path.exists(file_production))
        with open(file_production, 'r') as fp:
            content = fp.read()
        self.assertEqual(content, """\
-r base.txt

django-cors-headers==2.4.0
gunicorn==19.9.0
""")
        self.assertFalse(mock_configure_docker.called)
        self.assertFalse(mock_configure_drone_ci.called)
        self.assertFalse(mock_configure_docker_registry.called)
        mock_prettyprint.msg_blue.assert_called_with(
            'Great! Now you can find your new project inside the current\'s '
            'wizard folder with name "{}"'.format(self.name_project))

    @patch('service_builder.setup_service._configure_docker')
    @patch('service_builder.setup_service.yes_or_no')
    @patch('service_builder.setup_service.get_input')
    def test_setup_successful_w_docker(self, mock_get_input, mock_yn,
                                       mock_configure_docker):
        mock_get_input.side_effect = [self.name_project, self.name_application]
        mock_yn.side_effect = [True, False, False]
        setup()
        self.assertTrue(mock_configure_docker.called)

    @patch('service_builder.setup_service._configure_docker_registry')
    @patch('service_builder.setup_service._configure_drone_ci')
    @patch('service_builder.setup_service._configure_docker')
    @patch('service_builder.setup_service.yes_or_no')
    @patch('service_builder.setup_service.get_input')
    def test_setup_successful_w_docker_registry(
            self, mock_get_input, mock_yn, _mock_configure_docker,
            mock_configure_drone_ci, mock_configure_docker_registry):
        mock_get_input.side_effect = [
            self.name_project,
            self.name_application,
            'registry.tola.io',
            'toladata',
        ]
        mock_yn.side_effect = [True, True, True]
        setup()
        self.assertTrue(mock_configure_drone_ci.called)
        self.assertTrue(mock_configure_docker_registry.called)

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
             'gunicorn -b 0.0.0.0:80 {}.wsgi'.format(self.name_project)),
            ('run-standalone-dev.sh', 'gunicorn -b 0.0.0.0:8080 --reload'),
            ('tcp-port-wait.sh', 'tcp-port-wait')
        )
        for filename, content_expected in filename_content_list:
            with open(filename, 'r') as file_tpl:
                content = file_tpl.read()
                self.assertIn(content_expected, content)
                self.assertNotIn('{{ name_project }}', content)


class SetupDockerRegistryTest(TestCase):
    def setUp(self):
        self.main_dir = os.getcwd()
        self.name_project = 'test_service'
        shutil.rmtree(self.name_project, ignore_errors=True)
        os.mkdir(self.name_project)
        os.chdir(self.name_project)

    def tearDown(self):
        os.chdir(self.main_dir)
        shutil.rmtree(self.name_project, ignore_errors=True)

    def test_configure_docker_registry(self):
        _configure_docker_registry(
            'test_service', 'registry.tola.io', 'toladata')
        with open('.drone.yml', 'r') as file_tpl:
            content = file_tpl.read()
            self.assertIn("""\
  build-docker-image-tag:
    image: plugins/docker
    insecure: true
    registry: registry.tola.io
    repo: registry.tola.io/toladata/test_service
    file: Dockerfile
    auto_tag: true
    secrets: [DOCKER_USERNAME, DOCKER_PASSWORD]
    when:
      event: [tag]
      status: [success]""", content)
