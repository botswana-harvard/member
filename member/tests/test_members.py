from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.db.utils import IntegrityError
from django.test import TestCase, tag

from edc_constants.constants import NO, DEAD, FEMALE, MALE, YES, REFUSED

from ..constants import (
    MENTAL_INCAPACITY, HEAD_OF_HOUSEHOLD, BLOCK_PARTICIPATION, ELIGIBLE_FOR_CONSENT,
    NOT_ELIGIBLE, ABSENT, UNDECIDED, DECEASED, HTC_ELIGIBLE)
from ..exceptions import EnumerationRepresentativeError, MemberEnrollmentError, MemberValidationError
from ..models import HouseholdMember, EnrollmentLoss, EnrollmentChecklist
from ..participation_status import ParticipationStatus

from .test_mixins import MemberMixin


class TestMembers(MemberMixin, TestCase):

    def test_cannot_add_first_member_if_not_hoh(self):
        """Assert cannot add first member if not head of household."""
        household_structure = self.make_household_ready_for_enumeration(make_hoh=False)
        self.assertRaises(
            EnumerationRepresentativeError,
            mommy.make_recipe,
            'member.householdmember',
            household_structure=household_structure,
            relation='Mother')

    def test_can_add_first_member_if_hoh(self):
        """Assert can add head of household."""
        household_structure = self.make_household_ready_for_enumeration(make_hoh=False)
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            relation=HEAD_OF_HOUSEHOLD)
        self.assertTrue(household_member.eligible_member)

    def test_add_hoh_member_in_different_households(self):
        """Asserts adding a HoH to one household does not block all households."""
        household_structure = self.make_household_ready_for_enumeration(make_hoh=False)
        mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            relation=HEAD_OF_HOUSEHOLD)
        try:
            self.make_household_ready_for_enumeration(make_hoh=True)
        except EnumerationRepresentativeError:
            self.fail('EnumerationRepresentativeError unexpectedly raised')

    def test_cannot_add_more_members_if_no_hoh_eligibility(self):
        """Assert can add head of household."""
        household_structure = self.make_household_ready_for_enumeration(make_hoh=False)
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

    def test_can_add_more_members_if_hoh_eligibility(self):
        """Assert can add head of household."""
        household_structure = self.make_household_ready_for_enumeration(make_hoh=False)
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

    def test_create_member_raises_on_dead_but_present(self):
        household_structure = self.make_household_ready_for_enumeration()
        self.assertRaises(
            MemberValidationError,
            mommy.make_recipe,
            'member.householdmember',
            household_structure=household_structure,
            survival_status=DEAD,
            present_today=YES)

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
            survival_status=DEAD,
            present_today=NO)
        self.assertFalse(household_member.eligible_member)

    # test enrollment checklist matches its houehold member
    def test_enrollment_checklist(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
        )

    def test_enrollment_checklist_to_household_member_age_mismatch(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            age_in_years=25)
        self.assertEqual(household_member.age_in_years, 25)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            dob=(self.get_utcnow() - relativedelta(years=35)).date())

    def test_enrollment_checklist_to_household_member_initials_mismatch(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            initials='AA')
        self.assertEqual(household_member.initials, 'AA')
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            initials='XX')

    def test_enrollment_checklist_to_household_member_resident_mismatch(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            study_resident=YES)
        self.assertEqual(household_member.study_resident, YES)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            part_time_resident=NO)

    def test_enrollment_checklist_to_household_member_gender_mismatch(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            gender=MALE)
        self.assertEqual(household_member.gender, MALE)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            gender=FEMALE)

    # test enrollment loss / ineligible by the enrollment checklist
    def test_enrollment_checklist_eligible(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials)            
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(enrollment_checklist.is_eligible)
        self.assertFalse(enrollment_checklist.loss_reason)
        self.assertTrue(household_member.eligible_subject)
        self.assertTrue(household_member.enrollment_checklist_completed)
        self.assertFalse(household_member.enrollment_loss_completed)

    def test_enrollment_checklist_ineligible_by_age_raises(self):
        """Asserts cannot enter EnrollmentChecklist because member is not eligible for screening by age."""
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            age_in_years=10)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            dob=(self.get_utcnow() - relativedelta(years=10)).date())

    def test_enrollment_checklist_ineligible_no_identity(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            has_identity=NO)
        self.assertIn('identity', enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_household_residency(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            household_residency=NO)
        self.assertIn('household residency', enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_part_time_resident(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            part_time_resident=NO)

    def test_enrollment_checklist_ineligible_by_citizenship1(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            citizen=NO,
            legal_marriage=NO)
        self.assertIn('Not a citizen and not married to a citizen', enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_citizenship2(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            citizen=NO,
            legal_marriage=YES,
            marriage_certificate=NO)
        self.assertIn(
            'Not a citizen, married to a citizen but does not have a marriage certificate',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_literacy(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            literacy=NO)
        self.assertIn(
            'Illiterate with no literate witness',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_blocked_participation(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            confirm_participation=BLOCK_PARTICIPATION)
        self.assertIn(
            'Already enrolled',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_minor_no_guardian(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            age_in_years=17)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            dob=(self.get_utcnow() - relativedelta(years=17)).date(),
            guardian=NO)
        self.assertIn(
            'Minor without guardian available',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_creates_loss_on_ineligible(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            literacy=NO)
        try:
            EnrollmentLoss.objects.get(household_member=household_member)
        except EnrollmentLoss.DoesNotExist:
            self.fail('EnrollmentLoss.DoesNotExist unexpectedly raised.')

    def test_enrollment_checklist_does_not_create_loss_on_eligible(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials)
        try:
            EnrollmentLoss.objects.get(household_member=household_member)
            self.fail('EnrollmentLoss.DoesNotExist unexpectedly NOT raised.')
        except EnrollmentLoss.DoesNotExist:
            pass

    def test_enrollment_checklist_creates_loss_on_ineligible2(self):
        """Asserts changing household meber to ineligible deletes EnrollmentChecklist."""
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            literacy=NO)
        try:
            EnrollmentLoss.objects.get(household_member=household_member)
        except EnrollmentLoss.DoesNotExist:
            self.fail('EnrollmentLoss.DoesNotExist unexpectedly raised.')
        household_member.study_resident = NO
        household_member.save()
        try:
            EnrollmentChecklist.objects.get(household_member=household_member)
            self.fail('EnrollmentChecklist.DoesNotExist unexpectedly NOT raised.')
        except EnrollmentChecklist.DoesNotExist:
            pass

    def test_enrollment_checklist_ineligible_updates_householdmember(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials,
            literacy=NO)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(household_member.enrollment_checklist_completed)
        self.assertTrue(household_member.enrollment_loss_completed)
        self.assertFalse(household_member.eligible_subject)

    def test_enrollment_checklist_eligible_updates_householdmember(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            initials=household_member.initials)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(household_member.enrollment_checklist_completed)
        self.assertFalse(household_member.enrollment_loss_completed)
        self.assertTrue(household_member.eligible_subject)

    # member status
    def test_member_status(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = HouseholdMember.objects.get(household_structure=household_structure)
        self.add_enrollment_checklist(household_member)
        self.assertEqual(household_member.member_status, ELIGIBLE_FOR_CONSENT)

    def test_member_status_ineligible(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            age_in_years=10)
        self.assertEqual(household_member.member_status, NOT_ELIGIBLE)

    def test_member_status_for_absent(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        household_member = self.make_absent_member(household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, ABSENT)

    def test_member_status_for_refused(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        household_member = self.make_refused_member(household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, REFUSED)

    def test_member_status_for_undecided(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        household_member = self.make_undecided_member(household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, UNDECIDED)

    def test_member_status_for_deceased(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        household_member = self.make_deceased_member(household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, DECEASED)

    def test_member_status_for_htc_eligible(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        household_member = self.make_htc_member(household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, HTC_ELIGIBLE)

    def test_member_visit_attempts(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=self.get_utcnow() - relativedelta(weeks=1))
        household_member = self.make_absent_member(
            household_member=household_member,
            report_date=(self.get_utcnow() - relativedelta(weeks=1)).date())
        household_member = self.make_absent_member(
            household_member=household_member,
            report_date=(self.get_utcnow() - relativedelta(days=4)).date())
        household_member = self.make_absent_member(
            household_member=household_member,
            report_date=(self.get_utcnow() - relativedelta(days=2)).date())
        self.assertEqual(household_member.visit_attempts, 3)

    def test_absent_uniqueness(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=self.get_utcnow() - relativedelta(weeks=1))
        household_member = self.make_absent_member(household_member=household_member)
        self.assertRaises(
            IntegrityError,
            self.make_absent_member,
            household_member=household_member)

    def test_undecided_uniqueness(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=self.get_utcnow() - relativedelta(weeks=1))
        household_member = self.make_undecided_member(household_member=household_member)
        self.assertRaises(
            IntegrityError,
            self.make_undecided_member,
            household_member=household_member)

    @tag('me')
    def test_internal_and_subject_identifier(self):
        household_structure = self.make_household_ready_for_enumeration(make_hoh=False)
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            relation=HEAD_OF_HOUSEHOLD)
        subject_identifier = household_member.subject_identifier
        subject_identifier_as_pk = household_member.subject_identifier_as_pk
        self.assertIsNotNone(subject_identifier)
        self.assertIsNotNone(subject_identifier_as_pk)
        self.assertEqual(subject_identifier, subject_identifier_as_pk)
        self.assertIsNotNone(household_member.internal_identifier)
        household_member.save()
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertEqual(subject_identifier, household_member.subject_identifier)
        self.assertEqual(subject_identifier_as_pk, household_member.subject_identifier_as_pk)
