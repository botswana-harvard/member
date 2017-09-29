from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.apps import apps as django_apps
from django.db.utils import IntegrityError
from django.test import TestCase

from edc_constants.constants import NO, DEAD, YES, UUID_PATTERN, ALIVE, FEMALE,\
    NOT_APPLICABLE
from edc_map.site_mappers import site_mappers

from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from household.exceptions import HouseholdLogRequired
from household.tests import HouseholdTestHelper
from household.models import HouseholdStructure
from survey.tests import SurveyTestHelper
from survey.site_surveys import site_surveys

from ..constants import MENTAL_INCAPACITY, HEAD_OF_HOUSEHOLD, ABLE_TO_PARTICIPATE
from ..exceptions import EnumerationRepresentativeError
from ..models import HouseholdMember, MovedMember
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
        self.survey_schedule_object = site_surveys.get_survey_schedules()[0]
        self.household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False,
            report_datetime=self.survey_schedule_object.start)

    def test_add_first_member(self):
        self.member_helper.add_household_member(
            self.household_structure, relation=HEAD_OF_HOUSEHOLD)

    def test_add_first_member_raises_if_not_hoh(self):
        self.member_helper.add_household_member(
            self.household_structure, relation='husband')

    def test_cannot_add_another_member_without_hoh_eligibility(self):
        self.member_helper.add_household_member(
            self.household_structure, relation=HEAD_OF_HOUSEHOLD)
        self.assertRaises(
            EnumerationRepresentativeError,
            self.member_helper.add_household_member,
            self.household_structure, relation='husband')

    def test_add_another_member_when_hoh_eligibility_exists(self):
        """Assert can add head of household.
        """
        household_member = self.member_helper.add_household_member(
            self.household_structure, relation=HEAD_OF_HOUSEHOLD)
        # add householdheadeligibility
        mommy.make_recipe(
            'member.householdheadeligibility',
            household_member=household_member,
            report_datetime=household_member.report_datetime)
        # add another member, OK!
        self.member_helper.add_household_member(
            self.household_structure, relation='Mother')

    def test_add_ineligible_member_by_residency(self):
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=self.household_structure,
            report_datetime=self.household_structure.report_datetime,
            study_resident=NO)
        self.assertFalse(household_member.eligible_member)

    def test_add_ineligible_member_by_ability(self):
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=self.household_structure,
            report_datetime=self.household_structure.report_datetime,
            inability_to_participate=MENTAL_INCAPACITY)
        self.assertFalse(household_member.eligible_member)

    def test_add_ineligible_member_by_survival(self):
        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=self.household_structure,
            report_datetime=self.household_structure.report_datetime,
            survival_status=DEAD,
            present_today=NO)
        self.assertFalse(household_member.eligible_member)

    def test_absent_uniqueness(self):
        report_datetime = self.household_structure.survey_schedule_object.start
        household_member = self.member_helper.add_household_member(
            household_structure=self.household_structure,
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

    def test_moved_uniqueness(self):
        report_datetime = self.member_helper.get_utcnow()
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            report_datetime=report_datetime)
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_moved_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertRaises(
            IntegrityError,
            self.member_helper.make_moved_member,
            household_member=household_member,
            report_datetime=report_datetime)

    def test_moved_delete_on_not_applicable(self):
        report_datetime = self.member_helper.get_utcnow()
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            report_datetime=report_datetime)
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_moved_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(MovedMember.objects.all().count(), 1)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertEqual(household_member.has_moved, YES)
        self.assertTrue(household_member.moved)
        household_member.has_moved = NOT_APPLICABLE
        household_member.save()
        self.assertEqual(MovedMember.objects.all().count(), 0)

    def test_moved_delete_on_no(self):
        report_datetime = self.member_helper.get_utcnow()
        household_structure = self.member_helper.make_household_ready_for_enumeration(
            report_datetime=report_datetime)
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_moved_member(
            household_member=household_member,
            report_datetime=report_datetime)
        self.assertEqual(MovedMember.objects.all().count(), 1)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertEqual(household_member.has_moved, YES)
        self.assertTrue(household_member.moved)
        household_member.has_moved = NO
        household_member.save()
        self.assertEqual(MovedMember.objects.all().count(), 0)

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


class TestMembers2(TestCase):

    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()
    household_helper = HouseholdTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.survey_schedule_object = site_surveys.get_survey_schedules()[0]

    def test_cant_add_representative_eligibility_with_no_todays_log_entry(self):
        plot = self.household_helper.make_confirmed_plot(
            household_count=1,
            report_datetime=self.survey_schedule_object.start)
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


class TestMembers3(TestCase):

    """Assertions for subject identifier and internal identifier.
    """

    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()
    household_helper = HouseholdTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.survey_schedule_object = site_surveys.get_survey_schedules()[0]
        self.household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False,
            report_datetime=self.survey_schedule_object.start)
        self.defaults = dict(
            household_structure=self.household_structure,
            report_datetime=self.household_structure.report_datetime,
            first_name='NOAM',
            initials='NC',
            inability_to_participate=ABLE_TO_PARTICIPATE,
            survival_status=ALIVE,
            age_in_years=25,
            study_resident=YES,
            gender=FEMALE,
            relation=HEAD_OF_HOUSEHOLD)

    def test_subject_identifier_is_uuid_by_default(self):
        household_member = HouseholdMember.objects.create(**self.defaults)
        self.assertIsNotNone(household_member.subject_identifier)
        self.assertRegex(household_member.subject_identifier, UUID_PATTERN)

    def test_subject_identifier_pk_is_uuid_by_default(self):
        household_member = HouseholdMember.objects.create(**self.defaults)
        self.assertIsNotNone(household_member.subject_identifier_as_pk)
        self.assertRegex(
            str(household_member.subject_identifier_as_pk), UUID_PATTERN)

    def test_subject_identifier_pk_equals_subject_identifier_initially(self):
        household_member = HouseholdMember.objects.create(**self.defaults)
        self.assertEqual(household_member.subject_identifier,
                         household_member.subject_identifier_as_pk.hex)

    def test_internal_identifier_is_uuid_by_default(self):
        household_member = HouseholdMember.objects.create(**self.defaults)
        self.assertIsNotNone(household_member.internal_identifier)
        self.assertRegex(
            str(household_member.internal_identifier), UUID_PATTERN)

    def test_internal_identifier_does_not_change_on_save(self):
        household_member = HouseholdMember.objects.create(**self.defaults)
        internal_identifier = household_member.internal_identifier
        household_member.save()
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertEqual(internal_identifier,
                         household_member.internal_identifier)
