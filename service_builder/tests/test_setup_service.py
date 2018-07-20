import os
import shutil
from unittest import TestCase
from unittest.mock import patch

from django.core.management.base import CommandError

from ..setup_service import setup


class SetupTest(TestCase):
    def setUp(self):
        self.name_project = 'test_service'
        self.name_application = 'app'
        shutil.rmtree(self.name_project, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(self.name_project, ignore_errors=True)

    @patch('service_builder.setup_service.get_input')
    def test_setup_successful(self, mock_get_input):
        mock_get_input.side_effect = [self.name_project, self.name_application]
        setup()
        self.assertTrue(os.path.isdir(self.name_project))
        self.assertTrue(
            os.path.isdir(
                os.path.join(self.name_project, self.name_application)
            ))

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
