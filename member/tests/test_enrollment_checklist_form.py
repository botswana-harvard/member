from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_constants.constants import MALE, ALIVE, YES, NO
from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from ..constants import ABLE_TO_PARTICIPATE
from ..forms import HouseholdMemberForm
from .member_test_helper import MemberTestHelper
from .mappers import TestMapper


class TestHouseholdMemberForm(TestCase):

    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        household_structure = self.member_helper.make_household_ready_for_enumeration()

        self.options = {
            'household_identifier': household_structure.household.household_identifier,
            'internal_identifier': '343216789',
            'subject_identifier': '123456',
            'survey_schedule': household_structure.survey_schedule,
            'household_structure': household_structure.id,
            'household_log': household_structure.householdlog.id,
            'first_name': 'NEO',
            'initials': 'NJK',
            'relation': 'son',
            'gender': MALE,
            'age_in_years': 22,
            'survival_status': ALIVE,
            'present_today': YES,
            'inability_to_participate': ABLE_TO_PARTICIPATE,
            'inability_to_participate_other': None,
            'study_resident': NO,
            'personal_details_changed': NO,
            'visit_attempts': 3,
            'eligible_htc': True,
            'refused_htc': False,
            'htc': True,
            'target': 2,
            'auto_filled': False,
            'updated_after_auto_filled': False,
            'additional_key': None,
            'report_datetime': (household_structure.householdlog.
                                householdlogentry_set.all()[0].report_datetime),
        }

    def test_valid_form(self):
        form = HouseholdMemberForm(data=self.options)
        self.assertTrue(form.is_valid())

    def test_valid_initials(self):
        """Assert participant provided correct initials.
        """
        self.options.update(initials='BHJ')
        form = HouseholdMemberForm(data=self.options)
        self.assertFalse(form.is_valid())
        self.assertIn('initials', form._errors)
