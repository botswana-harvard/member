from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_base.utils import get_utcnow
from edc_map.site_mappers import site_mappers
from household.constants import REFUSED_ENUMERATION, NO_HOUSEHOLD_INFORMANT
from survey.tests import SurveyTestHelper

from ..constants import ELIGIBLE_REPRESENTATIVE_ABSENT
from ..forms import RepresentativeEligibilityForm
from .mappers import TestMapper
from .member_test_helper import MemberTestHelper
from household.tests.household_test_helper import HouseholdTestHelper


@tag('form')
class TestHouseholdMemberFormValidator(TestCase):

    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()
    household_helper = HouseholdTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        self.today_datetime = self.household_structure.report_datetime

    def test_representative_eligibility_with_representative_absent(self):
        household_structure = self.household_helper.make_household_structure()
        self.household_helper.add_enumeration_attempt(
            household_structure,
            report_datetime=get_utcnow(),
            household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
        options = {
            'household_structure': household_structure.id}
        form = RepresentativeEligibilityForm(data=options)
        self.assertFalse(form.is_valid())

    def test_representative_eligibility_with_no_household_informant(self):
        household_structure = self.household_helper.make_household_structure()
        self.household_helper.add_enumeration_attempt(
            household_structure,
            report_datetime=get_utcnow(),
            household_status=NO_HOUSEHOLD_INFORMANT)
        options = {
            'household_structure': household_structure.id}
        form = RepresentativeEligibilityForm(data=options)
        self.assertFalse(form.is_valid())

    def test_representative_eligibility_with_refused_enumeration(self):
        household_structure = self.household_helper.make_household_structure()
        self.household_helper.add_enumeration_attempt(
            household_structure,
            report_datetime=get_utcnow(),
            household_status=REFUSED_ENUMERATION)
        options = {
            'household_structure': household_structure.id}
        form = RepresentativeEligibilityForm(data=options)
        self.assertFalse(form.is_valid())
