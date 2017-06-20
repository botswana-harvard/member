from django.apps import apps as django_apps
from django.test import TestCase
from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from edc_map.site_mappers import site_mappers
from household.constants import REFUSED_ENUMERATION, ELIGIBLE_REPRESENTATIVE_PRESENT
from household.forms import HouseholdLogEntryForm
from household.models import HouseholdLog
from household.tests import HouseholdTestHelper
from survey.site_surveys import site_surveys
from survey.tests import SurveyTestHelper

from .mappers import TestMapper
from .member_test_helper import MemberTestHelper


class TestHousehold(TestCase):

    member_helper = MemberTestHelper()
    household_helper = HouseholdTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_refused_enumeration_fails_members_exist(self):
        household_structure = self.household_helper.make_household_structure()
        self.household_helper.add_enumeration_attempt(
            household_structure,
            report_datetime=self.member_helper.get_utcnow())

        mommy.make_recipe(
            'member.representativeeligibility',
            household_structure=household_structure
        )
        mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,)
        household_log = HouseholdLog.objects.get(
            household_structure=household_structure)

        options = {
            'household_status': REFUSED_ENUMERATION,
            'household_log': household_log.id,
            'report_datetime': self.member_helper.get_utcnow() + relativedelta(hours=3),
            'survey_schedule': site_surveys.get_survey_schedules(current=True)[0]
        }
        form = HouseholdLogEntryForm(data=options)
        self.assertFalse(form.is_valid())

    def test_eligible_member_present_saves(self):
        household_structure = self.make_household_structure()
        self.household_helper.add_enumeration_attempt(
            household_structure,
            report_datetime=self.member_helper.get_utcnow())

        mommy.make_recipe(
            'member.representativeeligibility',
            household_structure=household_structure
        )
        mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,)
        household_log = HouseholdLog.objects.get(
            household_structure=household_structure)

        options = {
            'household_status': ELIGIBLE_REPRESENTATIVE_PRESENT,
            'household_log': household_log.id,
            'report_datetime': self.member_helper.get_utcnow() + relativedelta(hours=3),
            'survey_schedule': site_surveys.get_survey_schedules(current=True)[0]
        }
        form = HouseholdLogEntryForm(data=options)
        self.assertTrue(form.is_valid())
