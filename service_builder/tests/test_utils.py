import os
import tempfile
from unittest import TestCase

from .. import utils


class ReplaceTextTest(TestCase):
    def setUp(self):
        self.fp = tempfile.NamedTemporaryFile(delete=False)
        self.fp.writelines(
            [b'first\n', b'DEBUG = True  # comment\n', b'Third\n'])
        self.fp.seek(0)

    def tearDown(self):
        self.fp.close()

    def test_replace_text(self):
        utils.replace_text(self.fp.name, 'DEBUG = True', 'DEBUG = False')
        with open(self.fp.name, 'r') as file_output:
            lines = file_output.readlines()
        self.assertEqual(
            lines, ['first\n', 'DEBUG = False  # comment\n', 'Third\n'])


class AddAfterVariableTest(TestCase):
    def _write_file(self, lines: list):
        fp = tempfile.NamedTemporaryFile(delete=False)
        fp.writelines(lines)
        fp.seek(0)
        return fp

    def test_add_after_variable_simple(self):
        fp = self._write_file(
            [b'ONE = 1\n', b'TWO = True\n', b'THREE = "Yes"\n'])
        utils.add_after_variable(fp.name, 'TWO', 'TWO_HALF = None\n')

        with open(fp.name, 'r') as file_output:
            lines = file_output.readlines()
            self.assertEqual(
                lines, ['ONE = 1\n', 'TWO = True\n', 'TWO_HALF = None\n',
                        'THREE = "Yes"\n'])

        fp.close()

    def test_add_after_variable_medium(self):
        fp = self._write_file(
            [
                b'ONE = 1\n',
                b'TWO = [\n',
                b'    "some",\n',
                b']\n',
                b'THREE = "Yes"\n'
            ])
        utils.add_after_variable(fp.name, 'TWO', 'TWO_HALF = None\n')

        with open(fp.name, 'r') as file_output:
            lines = file_output.readlines()
            self.assertEqual(
                lines, ['ONE = 1\n', 'TWO = [\n', '    "some",\n', ']\n',
                        'TWO_HALF = None\n', 'THREE = "Yes"\n'])

        fp.close()

    def test_add_after_variable_medium_one_liner_tuple(self):
        fp = self._write_file(
            [
                b'ONE = 1\n',
                b'TWO = [("some")]\n',
                b'THREE = "Yes"\n'
            ])
        utils.add_after_variable(fp.name, 'TWO', 'TWO_HALF = None\n')

        with open(fp.name, 'r') as file_output:
            lines = file_output.readlines()
            self.assertEqual(
                lines, ['ONE = 1\n', 'TWO = [("some")]\n',
                        'TWO_HALF = None\n', 'THREE = "Yes"\n'])

        fp.close()

    def test_add_after_variable_hard(self):
        fp = self._write_file(
            [
                b'ONE = 1\n',
                b'TWO = [\n',
                b'    ("some", \n',
                b'     "more"), \n',
                b']\n',
                b'THREE = "Yes"\n'
            ])
        utils.add_after_variable(fp.name, 'TWO', 'TWO_HALF = None\n')

        with open(fp.name, 'r') as file_output:
            lines = file_output.readlines()
            self.assertEqual(
                lines, ['ONE = 1\n', 'TWO = [\n', '    ("some", \n',
                        '     "more"), \n', ']\n', 'TWO_HALF = None\n',
                        'THREE = "Yes"\n'])

        fp.close()


class AppendToFileTest(TestCase):
    def setUp(self):
        self.fp = tempfile.NamedTemporaryFile(delete=False)
        self.fp.writelines(
            [b'first\n', b'second\n'])
        self.fp.seek(0)

    def tearDown(self):
        self.fp.close()

    def test_append_to_file(self):
        utils.append_to_file(self.fp.name, 'third\n')
        with open(self.fp.name, 'r') as file_output:
            lines = file_output.readlines()
        self.assertEqual(
            lines, ['first\n', 'second\n', 'third\n'])


class GetTemplateContextTest(TestCase):
    def test_get_template_content(self):
        filename_content_list = (
            (os.path.join('settings', 'base_appended.tpl'), 'REST_FRAMEWORK'),
            (os.path.join('settings', 'base_installedapps.tpl'),
             'INSTALLED_APPS'),
            (os.path.join('settings', 'production.tpl'), 'ALLOWED_HOSTS'),

            (os.path.join('html', 'maintenance', 'index.html'), 'Sorry'),
        )
        for filename, content_expected in filename_content_list:
            content = utils.get_template_content(filename)
            self.assertIn(content_expected, content)
