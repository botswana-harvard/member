from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.test import TestCase, tag

from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from household.exceptions import HouseholdLogRequired
from household.models import HouseholdLogEntry

from ..models import AbsentMember, UndecidedMember, RefusedMember

from .mixins import MemberMixin


class TestLogEntry(MemberMixin, TestCase):

    def test_todays_log_entry_or_raise_one_log(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        try:
            self.add_household_member(household_structure)
        except HouseholdLogRequired:
            self.fail('HouseholdLogRequired unexpectedly raised')

    def test_todays_log_entry_or_raise_tomorrow(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        obj = HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure).last()
        tomorrow = obj.report_datetime + relativedelta(days=1)
        self.assertRaises(
            HouseholdLogRequired,
            self.add_household_member,
            household_structure,
            report_datetime=tomorrow)

    def test_todays_log_entry_or_raise_multiple_log_entry(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        obj = HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure).last()
        tomorrow = obj.report_datetime + relativedelta(days=1)
        self.assertRaises(
            HouseholdLogRequired,
            self.add_household_member,
            household_structure,
            report_datetime=tomorrow)

    def test_todays_log_entry_or_raise_yesterday(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        obj = HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure).last()
        yesterday = obj.report_datetime - relativedelta(days=10)
        self.assertRaises(
            HouseholdLogRequired,
            self.add_household_member,
            household_structure,
            report_datetime=yesterday)

    def test_todays_log_entry_or_raise_absentmember(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        household_structure = self.add_enumeration_attempt(household_structure)
        obj = HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure).last()
        self.add_household_member(
            household_structure, report_datetime=obj.report_datetime)
        self.add_household_member(
            household_structure, report_datetime=obj.report_datetime)
        household_member = self.add_household_member(
            household_structure, report_datetime=obj.report_datetime)

        tomorrow = obj.report_datetime + relativedelta(days=1)

        self.assertRaises(
            HouseholdLogRequired,
            mommy.make_recipe,
            'member.absentmember',
            household_member=household_member,
            report_datetime=tomorrow)

    def test_todays_log_entry_or_raise_absentmember_ok(self):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=False)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        self.add_enumeration_attempt(household_structure)
        household_structure = self.add_enumeration_attempt(household_structure)
        obj = HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure).last()
        self.add_household_member(
            household_structure, report_datetime=obj.report_datetime)
        self.add_household_member(
            household_structure, report_datetime=obj.report_datetime)
        household_member = self.add_household_member(
            household_structure, report_datetime=obj.report_datetime)

        try:
            mommy.make_recipe(
                'member.absentmember',
                household_member=household_member,
                report_datetime=obj.report_datetime)
        except HouseholdLogRequired:
            self.fail('HouseholdLogRequired unexpectedly raised')

        absent_member = AbsentMember.objects.get(
            household_member=household_member,
            report_datetime=obj.report_datetime)
        absent_member.save()

    def test_add_model_requires_current_household_log_entry(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_structure.householdlog.householdlogentry_set.all().delete()
        report_datetime = household_structure.survey_schedule_object.start
        self.add_enumeration_attempt(
            household_structure=household_structure,
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT,
            report_datetime=report_datetime)
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        for func_name in [
                'make_absent_member',
                'make_undecided_member',
                'make_deceased_member',
                'make_refused_member',
                'make_moved_member']:
            self.assertRaises(
                HouseholdLogRequired,
                getattr(self, func_name),
                household_member=household_member,
                report_datetime=report_datetime + relativedelta(days=5))

    def test_change_model_requires_household_log_entry_for_report_datetime(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_structure.householdlog.householdlogentry_set.all().delete()
        report_datetime = household_structure.survey_schedule_object.start
        report_datetime = report_datetime - relativedelta(days=5)
        self.add_enumeration_attempt(
            household_structure=household_structure,
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT,
            report_datetime=report_datetime)
        household_member = self.add_household_member(
            household_structure=household_structure,
            report_datetime=report_datetime)
        self.make_absent_member(
            household_member, report_datetime=report_datetime)
        self.make_undecided_member(
            household_member, report_datetime=report_datetime)
        self.make_refused_member(
            household_member, report_datetime=report_datetime)
        absent_member = AbsentMember.objects.get(
            household_member__pk=household_member.pk)
        absent_member.save()
        undecided_member = UndecidedMember.objects.get(
            household_member__pk=household_member.pk)
        undecided_member.save()
        refused_member = RefusedMember.objects.get(
            household_member__pk=household_member.pk)
        refused_member.save()

    def test_todays_log_entry_or_raise_no_logs(self):
        household_structure = self.make_household_structure()
        self.assertEqual(HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure).count(), 0)
        mommy.make_recipe(
            'member.representativeeligibility',
            household_structure=household_structure)
        self.assertRaises(
            HouseholdLogRequired,
            self.add_household_member, household_structure)
