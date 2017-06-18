from django.test import TestCase, tag

from edc_constants.constants import REFUSED, NO

from ..constants import (
    ABSENT, UNDECIDED, DECEASED, HTC_ELIGIBLE, ELIGIBLE, INELIGIBLE)
from ..participation_status import ParticipationStatus
from .mixins import MemberMixin


@tag('PP')
class TestMembers(MemberMixin, TestCase):

    def test_member_status_for_eligible(self):
        household_structure = self.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.add_enrollment_checklist(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, ELIGIBLE)

    def test_member_status_for_ineligible(self):
        household_structure = self.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.add_enrollment_checklist(
            household_member=household_member,
            report_datetime=report_datetime,
            citizen=NO,
            legal_marriage=NO)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, INELIGIBLE)

    def test_member_status_for_absent(self):
        household_structure = self.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.make_absent_member(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, ABSENT)

    def test_member_status_for_refused(self):
        household_structure = self.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.make_refused_member(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, REFUSED)

    def test_member_status_for_undecided(self):
        household_structure = self.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.make_undecided_member(
            household_member=household_member,
            report_datetime=report_datetime)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, UNDECIDED)

    def test_member_status_for_deceased(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        household_member = self.make_deceased_member(
            household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, DECEASED)

    def test_member_status_for_htc_eligible(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = self.add_household_member(
            household_structure=household_structure)
        household_member = self.make_htc_member(
            household_member=household_member)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(
            participation_status.participation_status, HTC_ELIGIBLE)

    def test_member_status_for_ineligible_non_citizen(self):
        household_structure = self.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.add_enrollment_checklist(
            household_member=household_member,
            report_datetime=report_datetime,
            citizen=NO,
            legal_marriage=NO)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, INELIGIBLE)

    def test_member_status_for_ineligible2(self):
        household_structure = self.make_household_ready_for_enumeration()
        report_datetime = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last().report_datetime
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        household_member = self.make_undecided_member(
            household_member=household_member,
            report_datetime=report_datetime)
        household_member = self.make_absent_member(
            household_member=household_member,
            report_datetime=report_datetime)
        household_member = self.add_enrollment_checklist(
            household_member=household_member,
            report_datetime=report_datetime,
            citizen=NO,
            legal_marriage=NO)
        participation_status = ParticipationStatus(household_member)
        self.assertEqual(participation_status.participation_status, INELIGIBLE)
