from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.apps import apps as django_apps
from django.db.utils import IntegrityError
from django.test import TestCase, tag

from edc_constants.constants import NO, DEAD, YES
from edc_map.site_mappers import site_mappers

from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from household.exceptions import HouseholdLogRequired
from household.tests import HouseholdTestHelper
from household.models import HouseholdStructure
from survey.tests import SurveyTestHelper
from survey.site_surveys import site_surveys

from ..clone import Clone
from ..constants import MENTAL_INCAPACITY, HEAD_OF_HOUSEHOLD
from ..exceptions import EnumerationRepresentativeError, MemberValidationError
from ..models import HouseholdMember
from .member_test_helper import MemberTestHelper
from .mappers import TestMapper


class TestMembers(TestCase):

    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()
    household_helper = HouseholdTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_can_add_first_member_if_hoh(self):
        """Assert can add head of household.
        """
        survey_schedule_object = site_surveys.get_survey_schedules()[0]
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False,
            report_datetime=survey_schedule_object.start)
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            relation=HEAD_OF_HOUSEHOLD,
            report_datetime=household_structure.report_datetime)
        self.assertTrue(household_member.eligible_member)

    def test_cant_add_representative_eligibility_with_no_todays_log_entry(self):
        """Assert can not add representative eligibility without
        today's household log entry.
        """
        survey_schedule_object = site_surveys.get_survey_schedules()[0]
        plot = self.household_helper.make_confirmed_plot(
            household_count=1,
            report_datetime=survey_schedule_object.start)
        household_structures = HouseholdStructure.objects.filter(
            household__plot=plot)
        for household_structure in household_structures:
            mommy.make_recipe(
                'member.representativeeligibility',
                household_structure=household_structure)
            self.assertRaises(
                HouseholdLogRequired,
                mommy.make_recipe,
                'member.householdmember',
                household_structure=household_structure,
                relation=HEAD_OF_HOUSEHOLD,
                report_datetime=household_structure.report_datetime)

    def test_cannot_add_more_members_if_no_hoh_eligibility(self):
        """Assert can add head of household.
        """
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        self.member_helper.add_household_member(
            household_structure, relation=HEAD_OF_HOUSEHOLD)
        self.assertRaises(
            EnumerationRepresentativeError,
            mommy.make_recipe,
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            relation='Mother')

    def test_can_add_more_members_if_hoh_eligibility(self):
        """Assert can add head of household.
        """
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        household_member = self.member_helper.add_household_member(
            household_structure, relation=HEAD_OF_HOUSEHOLD)
        mommy.make_recipe(
            'member.householdheadeligibility',
            household_member=household_member,
            report_datetime=household_member.report_datetime)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(household_member.eligible_hoh)
        # add a second household member
        self.member_helper.add_household_member(
            household_structure, relation='Mother')

    def test_create_member(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            report_datetime=household_structure.report_datetime,
            household_structure=household_structure)
        self.assertTrue(household_member.eligible_member)

    def test_create_member_raises_on_dead_but_present(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        self.assertRaises(
            MemberValidationError,
            mommy.make_recipe,
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            survival_status=DEAD,
            present_today=YES)

    def test_create_ineligible_member_by_age_min(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            report_datetime=household_structure.report_datetime,
            household_structure=household_structure,
            age_in_years=15)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_age_max(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            age_in_years=65)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_residency(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            study_resident=NO)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_ability(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            inability_to_participate=MENTAL_INCAPACITY)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_survival(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            survival_status=DEAD,
            present_today=NO)
        self.assertFalse(household_member.eligible_member)

    def test_member_visit_attempts(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        report_datetime = household_structure.survey_schedule_object.start
        report_datetime = report_datetime + relativedelta(weeks=1)
        self.household_helper.add_enumeration_attempt(
            household_structure=household_structure,
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT,
            report_datetime=report_datetime)
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_absent_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(household_member.visit_attempts, 1)
        household_member = self.member_helper.make_undecided_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(household_member.visit_attempts, 2)
        household_member = self.member_helper.make_refused_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(household_member.visit_attempts, 3)
        household_member = self.member_helper.make_moved_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(household_member.visit_attempts, 4)

    def test_absent_uniqueness(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.survey_schedule_object.start
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_absent_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertRaises(
            IntegrityError,
            self.member_helper.make_absent_member,
            household_member=household_member,
            report_datetime=report_datetime)

    def test_undecided_uniqueness(self):
        report_datetime = self.member_helper.get_utcnow()
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            report_datetime=report_datetime)
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_undecided_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertRaises(
            IntegrityError,
            self.member_helper.make_undecided_member,
            household_member=household_member,
            report_datetime=report_datetime)

    def test_internal_and_subject_identifier(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            relation=HEAD_OF_HOUSEHOLD)
        subject_identifier = household_member.subject_identifier
        subject_identifier_as_pk = household_member.subject_identifier_as_pk
        self.assertIsNotNone(subject_identifier)
        self.assertIsNotNone(subject_identifier_as_pk)
        self.assertEqual(subject_identifier, subject_identifier_as_pk)
        self.assertIsNotNone(household_member.internal_identifier)
        household_member.save()
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertEqual(
            subject_identifier, household_member.subject_identifier)
        self.assertEqual(
            subject_identifier_as_pk, household_member.subject_identifier_as_pk)

    def test_plot_eligible_members_increments(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        self.assertEqual(
            household_structure.household.plot.eligible_members, 0)

    def test_add_members_updates_household_structure(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        for _ in range(0, 3):
            self.member_helper.add_household_member(
                household_structure=household_structure,
                report_datetime=household_structure.report_datetime
            )
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        self.assertTrue(household_structure.enumerated)
        self.assertIsNotNone(household_structure.enumerated_datetime)

    def test_delete_members_updates_household_structure(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        for _ in range(0, 3):
            self.member_helper.add_household_member(
                household_structure=household_structure,
                report_datetime=household_structure.report_datetime)
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        household_structure.householdmember_set.all().delete()
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        self.assertFalse(household_structure.enumerated)
        self.assertIsNone(household_structure.enumerated_datetime)

    def test_mixin_returns_household_structure_for_survey(self):
        for survey_schedule in site_surveys.get_survey_schedules(current=True):
            household_structure = self.member_helper.make_household_ready_for_enumeration(
                make_hoh=False, survey_schedule=survey_schedule)
            self.assertEqual(
                household_structure.survey_schedule, survey_schedule.field_value)

    def test_household_member_clone(self):
        survey_schedule = site_surveys.get_survey_schedules(current=True)[0]
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False, survey_schedule=survey_schedule)
        self.member_helper.add_household_member(
            household_structure=household_structure)
        self.member_helper.add_household_member(
            household_structure=household_structure)
        self.member_helper.add_household_member(
            household_structure=household_structure)
        next_household_structure = self.member_helper.get_next_household_structure_ready(
            household_structure, make_hoh=None)
        previous_members = HouseholdMember.objects.filter(
            household_structure=household_structure).order_by('report_datetime')
        for obj in previous_members:
            new_obj = obj.clone(
                household_structure=next_household_structure,
                report_datetime=next_household_structure.report_datetime,
                user_created='erikvw')
            self.assertEqual(
                obj.internal_identifier, new_obj.internal_identifier)
            self.assertEqual(
                obj.subject_identifier, new_obj.subject_identifier)
            new_obj.save()
            new_obj = HouseholdMember.objects.get(pk=new_obj.pk)
            self.assertEqual(
                obj.internal_identifier, new_obj.internal_identifier)
            self.assertEqual(
                obj.subject_identifier, new_obj.subject_identifier)

    def test_clone_members_none(self):
        survey_schedule = site_surveys.get_survey_schedules(current=True)[0]
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False, survey_schedule=survey_schedule)
        next_household_structure = self.member_helper.get_next_household_structure_ready(
            household_structure, make_hoh=False)
        clone = Clone(
            household_structure=next_household_structure,
            report_datetime=household_structure.report_datetime)
        self.assertEqual(clone.members.all().count(), 0)

    def test_clone_members_no_previous(self):
        survey_schedule = site_surveys.get_survey_schedules(current=True)[0]
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False, survey_schedule=survey_schedule)
        next_household_structure = self.member_helper.get_next_household_structure_ready(
            household_structure, make_hoh=False)
        clone = Clone(
            household_structure=next_household_structure,
            report_datetime=household_structure.report_datetime)
        self.assertEqual(clone.members.all().count(), 0)
