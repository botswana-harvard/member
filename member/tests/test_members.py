from django.test import TestCase, tag
from model_mommy import mommy

from edc_constants.constants import NO, DEAD

from ..constants import MENTAL_INCAPACITY

from .test_mixins import MemberMixin
from member.constants import HEAD_OF_HOUSEHOLD
from member.exceptions import EnumerationRepresentativeError
from member.models.household_member import HouseholdMember


class TestMembers(MemberMixin, TestCase):

    def test_cannot_add_first_member_if_not_hoh(self):
        """Assert cannot add first member if not head of household."""
        household_structure = self.make_household_ready_for_enumeration(make_hod=False)
        self.assertRaises(
            EnumerationRepresentativeError,
            mommy.make_recipe,
            'member.householdmember',
            household_structure=household_structure,
            relation='Mother')

    def test_can_add_first_member_if_hoh(self):
        """Assert can add head of household."""
        household_structure = self.make_household_ready_for_enumeration(make_hod=False)
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            relation=HEAD_OF_HOUSEHOLD)
        self.assertTrue(household_member.eligible_member)

    def test_cannot_add_more_members_if_no_hoh_eligibility(self):
        """Assert can add head of household."""
        household_structure = self.make_household_ready_for_enumeration(make_hod=False)
        mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            relation=HEAD_OF_HOUSEHOLD)
        self.assertRaises(
            EnumerationRepresentativeError,
            mommy.make_recipe,
            'member.householdmember',
            household_structure=household_structure,
            relation='Mother')

    @tag('me')
    def test_can_add_more_members_if_hoh_eligibility(self):
        """Assert can add head of household."""
        household_structure = self.make_household_ready_for_enumeration(make_hod=False)
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            relation=HEAD_OF_HOUSEHOLD)
        mommy.make_recipe(
            'member.householdheadeligibility',
            household_member=household_member)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(household_member.eligible_hoh)
        # add a second household member
        mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            relation='Mother')

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
