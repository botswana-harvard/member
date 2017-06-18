from django.test import TestCase

from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from household.models import HouseholdLog
from household.constants import REFUSED_ENUMERATION, ELIGIBLE_REPRESENTATIVE_PRESENT
from survey.site_surveys import site_surveys
from household.forms import HouseholdLogEntryForm


class TestHousehold(TestCase):
    def test_refused_enumeration_fails_members_exist(self):
        household_structure = self.make_household_structure()
        self.add_enumeration_attempt(household_structure,
                                     report_datetime=self.get_utcnow())

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
            'report_datetime': self.get_utcnow() + relativedelta(hours=3),
            'survey_schedule': site_surveys.get_survey_schedules(current=True)[0]
        }
        form = HouseholdLogEntryForm(data=options)
        self.assertFalse(form.is_valid())

    def test_eligible_member_present_saves(self):
        household_structure = self.make_household_structure()
        self.add_enumeration_attempt(household_structure,
                                     report_datetime=self.get_utcnow())

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
            'report_datetime': self.get_utcnow() + relativedelta(hours=3),
            'survey_schedule': site_surveys.get_survey_schedules(current=True)[0]
        }
        form = HouseholdLogEntryForm(data=options)
        self.assertTrue(form.is_valid())
