from django.test import TestCase, tag
from model_mommy import mommy

from edc_constants.constants import NO, DEAD

from ..constants import MENTAL_INCAPACITY

from .test_mixins import MemberMixin


class TestMembers(MemberMixin, TestCase):

    def test_create_member(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure)
        self.assertTrue(household_member.eligible_member)

    def test_create_ineligible_member_by_age_min(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            age_in_years=15)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_age_max(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            age_in_years=65)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_residency(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            study_resident=NO)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_ability(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            inability_to_participate=MENTAL_INCAPACITY)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_survival(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            survival_status=DEAD)
        self.assertFalse(household_member.eligible_member)
