from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.db.utils import IntegrityError
from django.test import TestCase, tag

from edc_constants.constants import NO, DEAD, YES

from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from household.exceptions import HouseholdLogRequired
from household.models import HouseholdStructure, Household
from survey.site_surveys import site_surveys

from ..clone import Clone
from ..constants import MENTAL_INCAPACITY, HEAD_OF_HOUSEHOLD
from ..exceptions import (
    EnumerationRepresentativeError,
    MemberValidationError, CloneError)
from ..models import HouseholdMember

from .mixins import MemberMixin


class TestMembers(MemberMixin, TestCase):

    def test_can_add_first_member_if_hoh(self):
        """Assert can add head of household.
        """
        survey_schedule_object = site_surveys.get_survey_schedules()[0]
        household_structure = self.make_household_ready_for_enumeration(
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
        plot = self.make_confirmed_plot(
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
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        self.add_household_member(
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
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        household_member = self.add_household_member(
            household_structure, relation=HEAD_OF_HOUSEHOLD)
        mommy.make_recipe(
            'member.householdheadeligibility',
            household_member=household_member,
            report_datetime=household_member.report_datetime)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(household_member.eligible_hoh)
        # add a second household member
        self.add_household_member(household_structure, relation='Mother')

    def test_create_member(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            report_datetime=household_structure.report_datetime,
            household_structure=household_structure)
        self.assertTrue(household_member.eligible_member)

    def test_create_member_raises_on_dead_but_present(self):
        household_structure = self.make_household_ready_for_enumeration()
        self.assertRaises(
            MemberValidationError,
            mommy.make_recipe,
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            survival_status=DEAD,
            present_today=YES)

    def test_create_ineligible_member_by_age_min(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            report_datetime=household_structure.report_datetime,
            household_structure=household_structure,
            age_in_years=15)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_age_max(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            age_in_years=65)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_residency(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            study_resident=NO)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_ability(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            inability_to_participate=MENTAL_INCAPACITY)
        self.assertFalse(household_member.eligible_member)

    def test_create_ineligible_member_by_survival(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            survival_status=DEAD,
            present_today=NO)
        self.assertFalse(household_member.eligible_member)

    def test_member_visit_attempts(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        report_datetime = household_structure.survey_schedule_object.start
        report_datetime = report_datetime + relativedelta(weeks=1)
        self.add_enumeration_attempt(
            household_structure=household_structure,
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT,
            report_datetime=report_datetime)
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.make_absent_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(household_member.visit_attempts, 1)
        household_member = self.make_undecided_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(household_member.visit_attempts, 2)
        household_member = self.make_refused_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(household_member.visit_attempts, 3)
        household_member = self.make_moved_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(household_member.visit_attempts, 4)

    def test_absent_uniqueness(self):
        household_structure = self.make_household_ready_for_enumeration()
        report_datetime = household_structure.survey_schedule_object.start
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.make_absent_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertRaises(
            IntegrityError,
            self.make_absent_member,
            household_member=household_member,
            report_datetime=report_datetime)

    def test_undecided_uniqueness(self):
        report_datetime = self.get_utcnow()
        household_structure = self.make_household_ready_for_enumeration(
            report_datetime=report_datetime)
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.make_undecided_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertRaises(
            IntegrityError,
            self.make_undecided_member,
            household_member=household_member,
            report_datetime=report_datetime)

    def test_internal_and_subject_identifier(self):
        household_structure = self.make_household_ready_for_enumeration(
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
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        self.assertEqual(
            household_structure.household.plot.eligible_members, 0)

    def test_add_members_updates_household_structure(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        for _ in range(0, 3):
            self.add_household_member(
                household_structure=household_structure,
                report_datetime=household_structure.report_datetime
            )
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        self.assertTrue(household_structure.enumerated)
        self.assertIsNotNone(household_structure.enumerated_datetime)

    def test_delete_members_updates_household_structure(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        for _ in range(0, 3):
            self.add_household_member(
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
            household_structure = self.make_household_ready_for_enumeration(
                make_hoh=False, survey_schedule=survey_schedule)
            self.assertEqual(
                household_structure.survey_schedule, survey_schedule.field_value)

    def test_household_member_clone(self):
        survey_schedule = site_surveys.get_survey_schedules(current=True)[0]
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False, survey_schedule=survey_schedule)
        self.add_household_member(household_structure=household_structure)
        self.add_household_member(household_structure=household_structure)
        self.add_household_member(household_structure=household_structure)
        next_household_structure = self.get_next_household_structure_ready(
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
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False, survey_schedule=survey_schedule)
        next_household_structure = self.get_next_household_structure_ready(
            household_structure, make_hoh=False)
        clone = Clone(
            household_structure=next_household_structure,
            report_datetime=household_structure.report_datetime)
        self.assertEqual(clone.members.all().count(), 0)

    def test_clone_members_no_previous(self):
        survey_schedule = site_surveys.get_survey_schedules(current=True)[0]
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False, survey_schedule=survey_schedule)
        next_household_structure = self.get_next_household_structure_ready(
            household_structure, make_hoh=False)
        clone = Clone(
            household_structure=next_household_structure,
            report_datetime=household_structure.report_datetime)
        self.assertEqual(clone.members.all().count(), 0)


class TestCloneMembers(MemberMixin, TestCase):

    def setUp(self):
        super().setUp()

        self.assertEqual(
            len(site_surveys.get_survey_schedules(current=True)), 3)
        self.survey_schedule = site_surveys.get_survey_schedules(
            current=True)[0]

        # make first household structure (plot, household, ...)
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False, survey_schedule=self.survey_schedule)
        self.add_household_member(household_structure)
        self.add_household_member(household_structure)
        self.add_household_member(household_structure)
        # requery
        household_structure = HouseholdStructure.objects.get(
            id=household_structure.id)

        # get the next one
        next_household_structure = self.get_next_household_structure_ready(
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
