from django.apps import apps as django_apps
from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.test import TestCase, tag

from edc_constants.constants import NO, FEMALE, MALE, YES
from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from ..constants import BLOCK_PARTICIPATION
from ..exceptions import MemberEnrollmentError
from ..models import HouseholdMember, EnrollmentLoss, EnrollmentChecklist
from .member_test_helper import MemberTestHelper
from .mappers import TestMapper


class TestMembers(TestCase):

    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_enrollment_checklist(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
        )

    def test_enrollment_checklist_to_household_member_age_mismatch(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            age_in_years=25)
        self.assertEqual(household_member.age_in_years, 25)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            initials=household_member.initials,
            dob=(household_structure.survey_schedule_object.start
                 - relativedelta(years=35)).date())

    def test_enrollment_checklist_to_household_member_initials_mismatch(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            initials='AA')
        self.assertEqual(household_member.initials, 'AA')
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            report_datetime=household_structure.report_datetime,
            initials='XX')

    def test_enrollment_checklist_to_household_member_resident_mismatch(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            study_resident=YES)
        self.assertEqual(household_member.study_resident, YES)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            part_time_resident=NO)

    def test_enrollment_checklist_to_household_member_gender_mismatch(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            gender=MALE)
        self.assertEqual(household_member.gender, MALE)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            initials=household_member.initials,
            gender=FEMALE)

    # test enrollment loss / ineligible by the enrollment checklist
    def test_enrollment_checklist_eligible(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(enrollment_checklist.is_eligible)
        self.assertFalse(enrollment_checklist.loss_reason)
        self.assertTrue(household_member.eligible_subject)
        self.assertTrue(household_member.enrollment_checklist_completed)
        self.assertFalse(household_member.enrollment_loss_completed)

    def test_enrollment_checklist_ineligible_by_age_raises(self):
        """Asserts cannot enter EnrollmentChecklist because
        member is not eligible for screening by age.
        """
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            age_in_years=10)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            initials=household_member.initials,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender)

    def test_enrollment_checklist_ineligible_no_identity(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            has_identity=NO)
        self.assertIn('identity', enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_household_residency(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            household_residency=NO)
        self.assertIn('household residency', enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_part_time_resident(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        self.assertRaises(
            MemberEnrollmentError,
            mommy.make_recipe,
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            part_time_resident=NO)

    def test_enrollment_checklist_ineligible_by_citizenship1(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            citizen=NO,
            legal_marriage=NO)
        self.assertIn(
            'Not a citizen and not married to a citizen',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_citizenship2(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            citizen=NO,
            legal_marriage=YES,
            marriage_certificate=NO)
        self.assertIn(
            'Not a citizen, married to a citizen but does '
            'not have a marriage certificate',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_literacy(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            literacy=NO)
        self.assertIn(
            'Illiterate with no literate witness',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_blocked_participation(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            confirm_participation=BLOCK_PARTICIPATION)
        self.assertIn(
            'Already enrolled',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_ineligible_by_minor_no_guardian(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=household_structure.report_datetime,
            age_in_years=17)
        enrollment_checklist = mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            initials=household_member.initials,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            guardian=NO)
        self.assertIn(
            'Minor without guardian available',
            enrollment_checklist.loss_reason)

    def test_enrollment_checklist_creates_loss_on_ineligible(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            literacy=NO)
        try:
            EnrollmentLoss.objects.get(household_member=household_member)
        except EnrollmentLoss.DoesNotExist:
            self.fail('EnrollmentLoss.DoesNotExist unexpectedly raised.')

    def test_enrollment_checklist_does_not_create_loss_on_eligible(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials)
        try:
            EnrollmentLoss.objects.get(household_member=household_member)
            self.fail('EnrollmentLoss.DoesNotExist unexpectedly NOT raised.')
        except EnrollmentLoss.DoesNotExist:
            pass

    def test_enrollment_checklist_creates_loss_on_ineligible2(self):
        """Asserts changing household meber to ineligible
        deletes EnrollmentChecklist.
        """
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
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
            self.fail(
                'EnrollmentChecklist.DoesNotExist unexpectedly NOT raised.')
        except EnrollmentChecklist.DoesNotExist:
            pass

    def test_enrollment_checklist_ineligible_updates_householdmember(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials,
            literacy=NO)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(household_member.enrollment_loss_completed)
        self.assertTrue(household_member.enrollment_checklist_completed)
        self.assertFalse(household_member.eligible_subject)

    def test_enrollment_checklist_eligible_updates_householdmember(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            report_datetime=household_structure.report_datetime,
            dob=(household_structure.report_datetime -
                 relativedelta(years=household_member.age_in_years)).date(),
            gender=household_member.gender,
            initials=household_member.initials)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(household_member.enrollment_checklist_completed)
        self.assertFalse(household_member.enrollment_loss_completed)
        self.assertTrue(household_member.eligible_subject)
