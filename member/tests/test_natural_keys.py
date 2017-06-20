from django.apps import apps as django_apps
from django.test import TestCase

from edc_sync.tests import SyncTestHelper
from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from .mappers import TestMapper


class TestNaturalKey(TestCase):

    survey_helper = SurveyTestHelper()
    sync_helper = SyncTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_natural_key_attrs(self):
        self.sync_helper.sync_test_natural_key_attr('member')

    def test_get_by_natural_key_attr(self):
        self.sync_helper.sync_test_get_by_natural_key_attr('member')
