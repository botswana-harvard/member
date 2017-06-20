from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_base.utils import get_utcnow
from edc_map.site_mappers import site_mappers

from household.constants import NO_HOUSEHOLD_INFORMANT
from household.constants import REFUSED_ENUMERATION, ELIGIBLE_REPRESENTATIVE_ABSENT
from household.models import HouseholdStructure, Household
from household.tests import HouseholdTestHelper
from survey.site_surveys import site_surveys
from survey.tests import SurveyTestHelper

from ..clone import Clone
from ..exceptions import CloneError
from ..forms import RepresentativeEligibilityForm
from ..models import HouseholdMember
from .member_test_helper import MemberTestHelper
from .mappers import TestMapper


@tag('clone')
class TestCloneMembers(TestCase):

    household_helper = HouseholdTestHelper()
    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.assertEqual(
            len(site_surveys.get_survey_schedules(current=True)), 1)
        self.survey_schedule = site_surveys.get_survey_schedules(
            current=True)[0]

        # make first household structure (plot, household, ...)
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False, survey_schedule=self.survey_schedule)
        self.member_helper.add_household_member(household_structure)
        self.member_helper.add_household_member(household_structure)
        self.member_helper.add_household_member(household_structure)
        # requery
        household_structure = HouseholdStructure.objects.get(
            id=household_structure.id)

        # get the next one
        next_household_structure = self.member_helper.get_next_household_structure_ready(
            household_structure, make_hoh=False)
        self.household = Household.objects.get(
            pk=household_structure.household.pk)

        # get report_datetimes or log entry
        self.report_datetime = (
            household_structure.householdlog.
            householdlogentry_set.all().last().report_datetime)
        self.next_report_datetime = (
            next_household_structure.householdlog.
            householdlogentry_set.all().last().report_datetime)

    def test_clone_members(self):
        clone = Clone(
            household=self.household,
            survey_schedule=self.survey_schedule.next,
            report_datetime=self.next_report_datetime)
        self.assertEqual(clone.members.all().count(), 3)

    def test_clone_members_attrs(self):
        clone = Clone(
            household=self.household,
            survey_schedule=self.survey_schedule.next,
            report_datetime=self.survey_schedule.next.start)
        for member in clone.members.all():
            self.assertIsNotNone(member.first_name)
            self.assertIsNotNone(member.gender)
            self.assertIsNotNone(member.age_in_years)
            self.assertIsNotNone(member.internal_identifier)
            self.assertIsNotNone(member.subject_identifier)
            self.assertIsNotNone(member.subject_identifier_as_pk)
            self.assertTrue(member.auto_filled)
            self.assertIsNotNone(member.auto_filled_datetime)
            self.assertFalse(member.updated_after_auto_filled)

    def test_clone_members_create(self):
        clone = Clone(
            household=self.household,
            survey_schedule=self.survey_schedule.next,
            report_datetime=self.survey_schedule.next.start,
            create=False)
        # returns a list of non-persisted model instances
        for member in clone.members:
            member.save()

    def test_clone_members_internal_identifier(self):
        # get members from enumerated household_structure
        household_structure = self.household.householdstructure_set.get(
            survey_schedule=self.survey_schedule.field_value)
        members = HouseholdMember.objects.filter(
            household_structure=household_structure)
        members_internal_identifiers = [m.internal_identifier for m in members]
        members_internal_identifiers.sort()

        # clone members from enumerated household_structure
        clone = Clone(
            household=self.household,
            survey_schedule=self.survey_schedule.next,
            report_datetime=self.survey_schedule.next.start)
        new_members_internal_identifiers = [
            m.internal_identifier for m in clone.members.all()]
        new_members_internal_identifiers.sort()
        self.assertEqual(
            members_internal_identifiers, new_members_internal_identifiers)

    def test_next_household_member(self):
        household_structure = HouseholdStructure.objects.get(
            household=self.household,
            survey_schedule=self.survey_schedule.field_value)
        household_member = household_structure.householdmember_set.all().first()
        Clone(
            household_structure=household_structure.next,
            report_datetime=self.survey_schedule.next.start)
        try:
            next_household_member = HouseholdMember.objects.get(
                household_structure=household_structure.next,
                internal_identifier=household_member.internal_identifier)
        except HouseholdMember.DoesNotExist:
            self.fail('HouseholdMember.DoesNotExist unexpectedly raised. '
                      'household_structure={}'.format(household_structure))
        self.assertEqual(next_household_member, household_member.next)

    def test_next_household_member2(self):
        household_structure = HouseholdStructure.objects.get(
            household=self.household,
            survey_schedule=self.survey_schedule.field_value)
        Clone(
            household_structure=household_structure.next,
            report_datetime=self.survey_schedule.next.start)
        for household_member in household_structure.householdmember_set.all():
            self.assertEqual(
                household_member.internal_identifier,
                household_member.next.internal_identifier)
            self.assertNotEqual(household_member.pk, household_member.next.pk)

    def test_clone_bad_report_datetime_in_new_survey_schedule(self):
        household_structure = HouseholdStructure.objects.get(
            household=self.household,
            survey_schedule=self.survey_schedule.field_value)
        report_datetime = self.survey_schedule.next.start - \
            relativedelta(days=1)
        self.assertRaises(
            CloneError,
            Clone,
            household_structure=household_structure.next,
            report_datetime=report_datetime)

    def test_clone_good_report_datetime_in_new_survey_schedule(self):
        household_structure = HouseholdStructure.objects.get(
            household=self.household,
            survey_schedule=self.survey_schedule.field_value)
        report_datetime = self.survey_schedule.next.start
        try:
            Clone(
                household_structure=household_structure.next,
                report_datetime=report_datetime)
        except CloneError:
            self.fail('CloneError unexpectedly raised')

    def test_household_member_internal_identifier(self):
        survey_schedule = self.survey_schedule
        household_structure = HouseholdStructure.objects.get(
            household=self.household,
            survey_schedule=survey_schedule.field_value)
        household_member = household_structure.householdmember_set.all().first()
        self.assertIsNotNone(household_member.internal_identifier)

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
