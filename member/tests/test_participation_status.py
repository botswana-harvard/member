from django.apps import apps as django_apps
from django.test import TestCase

from edc_constants.constants import REFUSED, NO
from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from ..constants import (
    ABSENT, UNDECIDED, DECEASED, HTC_ELIGIBLE, ELIGIBLE, INELIGIBLE, MOVED)
from ..participation_status import ParticipationStatus
from ..models import HouseholdMember
from .mappers import TestMapper
from .member_test_helper import MemberTestHelper


class TestMembers(TestCase):

    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)

    def test_member_status_for_eligible(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.add_enrollment_checklist(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, ELIGIBLE)

    def test_member_status_for_ineligible(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.add_enrollment_checklist(
            household_member=household_member,
            report_datetime=report_datetime,
            citizen=NO,
            legal_marriage=NO)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, INELIGIBLE)

    def test_member_status_for_absent(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_absent_member(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, ABSENT)

    def test_member_status_for_moved(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_moved_member(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, MOVED)
        household_member = HouseholdMember.objects.get(pk=household_member.pk)
        self.assertTrue(household_member.moved)

    def test_member_status_for_refused(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_refused_member(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, REFUSED)

    def test_member_status_for_undecided(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_undecided_member(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, UNDECIDED)

    def test_member_status_for_deceased(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        household_member = self.member_helper.make_deceased_member(
            household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, DECEASED)

    def test_member_status_for_htc_eligible(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure)
        household_member = self.member_helper.make_htc_member(
            household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(
            participation_status.participation_status, HTC_ELIGIBLE)

    def test_member_status_for_ineligible_non_citizen(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.add_enrollment_checklist(
            household_member=household_member,
            report_datetime=report_datetime,
            citizen=NO,
            legal_marriage=NO)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, INELIGIBLE)

    def test_member_status_for_ineligible2(self):
        household_structure = self.member_helper.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.member_helper.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_undecided_member(
            household_member=household_member,
            report_datetime=report_datetime)
        household_member = self.member_helper.make_absent_member(
            household_member=household_member,
            report_datetime=report_datetime)
        household_member = self.member_helper.add_enrollment_checklist(
            household_member=household_member,
            report_datetime=report_datetime,
            citizen=NO,
            legal_marriage=NO)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, INELIGIBLE)
