import os
import re
from unittest import TestCase

import django


class RequirementsTest(TestCase):
    def test_django_version_requirements_match(self):
        major, minor, patch, _, _ = django.VERSION
        django_version_expected = '{}.{}.{}'.format(major, minor, patch)
        requirements = os.path.join(
            'service_builder', 'templates', 'requirements', 'base.txt')
        with open(requirements, 'r') as file_output:
            content = file_output.read()
            res = re.split(r'Django~=(.+)\n', content)
            django_version = res[1]
            self.assertEqual(django_version, django_version_expected,
                             'The Django version running for this test does '
                             'not match the version found on the '
                             'service_builder requirements.')
