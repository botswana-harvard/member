from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_map.site_mappers import site_mappers
from survey.site_surveys import site_surveys
from survey.tests.survey_test_helper import SurveyTestHelper

from .mappers import TestMapper
from .member_test_helper import MemberTestHelper
from household.tests import HouseholdTestHelper


@tag('survey')
class TestSurvey(TestCase):

    """Tests to assert survey attrs."""

    member_helper = MemberTestHelper()
    household_helper = HouseholdTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_household_member(self):
        survey_schedule = site_surveys.get_survey_schedules(
            current=True)[0]
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            survey_schedule=survey_schedule)

        household_member = self.member_helper.add_household_member(
            household_structure)

        self.assertIsNotNone(household_member.survey_schedule)
        self.assertIsNotNone(household_member.survey_schedule_object)
        self.assertRaises(
            AttributeError, getattr, household_member, 'survey')
        self.assertRaises(
            AttributeError, getattr, household_member, 'survey_object')

    def test_household_member_survey_schedule_set_correctly(self):

        survey_schedules = site_surveys.get_survey_schedules(
            group_name='test_survey')

        if not survey_schedules:
            raise AssertionError('survey_schedules is unexpectedly None')

        for index, survey_schedule in enumerate(
                site_surveys.get_survey_schedules(group_name='test_survey')):
            with self.subTest(index=index, survey_schedule=survey_schedule):
                household_structure = self.member_helper.make_household_ready_for_enumeration(
                    survey_schedule=survey_schedule)
                household_member = self.member_helper.add_household_member(
                    household_structure)
                self.assertEqual(
                    household_member.survey_schedule,
                    'test_survey.year-{}.test_community'.format(index + 1))
                self.assertEqual(
                    household_member.survey_schedule_object.field_value,
                    'test_survey.year-{}.test_community'.format(index + 1))
                self.assertEqual(
                    household_member.survey_schedule_object.name,
                    'year-{}'.format(index + 1))
                self.assertEqual(
                    household_member.survey_schedule_object.group_name,
                    'test_survey')
                self.assertEqual(
                    household_member.survey_schedule_object.short_name,
                    'test_survey.year-{}'.format(index + 1))
