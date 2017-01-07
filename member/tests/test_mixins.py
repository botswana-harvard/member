from faker import Faker
from model_mommy import mommy

from edc_base_test.mixins import LoadListDataMixin
from edc_constants.constants import MALE

from household.models import HouseholdStructure, HouseholdLogEntry
from household.tests.test_mixins import HouseholdMixin

from ..constants import HEAD_OF_HOUSEHOLD
from ..list_data import list_data
from ..models import HouseholdMember


fake = Faker()


class MemberTestMixin(HouseholdMixin, LoadListDataMixin):

    list_data = list_data


class MemberMixin(MemberTestMixin):

    def setUp(self):
        super(MemberMixin, self).setUp()
        self.study_site = '40'

    def make_household_ready_for_enumeration(self, make_hoh=None, survey=None):
        """Returns household_structure after adding representative eligibility."""
        make_hoh = True if make_hoh is None else make_hoh
        household_structure = super().make_household_ready_for_enumeration(survey=survey)
        household_log_entry = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last()
        # add representative eligibility
        mommy.make_recipe(
            'member.representativeeligibility',
            report_datetime=household_log_entry.report_datetime,
            household_structure=household_structure)
        if make_hoh:
            first_name = fake.first_name()
            last_name = fake.last_name()
            household_member = mommy.make_recipe(
                'member.householdmember',
                household_structure=household_structure,
                report_datetime=household_log_entry.report_datetime,
                first_name=first_name,
                initials=first_name[0] + last_name[0],
                relation=HEAD_OF_HOUSEHOLD)
            mommy.make_recipe(
                'member.householdheadeligibility',
                report_datetime=household_log_entry.report_datetime,
                household_member=household_member)
        return household_structure

    # def make_next_household_ready_for_enumeration(self, household_structure):

    def make_enumerated_household_with_male_member(self):
        household_structure = self.make_household_ready_for_enumeration()
        household_member = household_structure.householdmember_set.all()[0]
        household_member.gender = MALE
        household_member.save()
        household_structure = HouseholdStructure.objects.get(pk=household_structure.pk)
        return household_structure

    def add_household_member(self, household_structure, **options):
        """Returns a household member that is by default eligible."""
        first_name = fake.first_name()
        last_name = fake.last_name()
        if not options.get('report_datetime'):
            household_log_entry = HouseholdLogEntry.objects.filter(
                household_log__household_structure=household_structure).order_by('report_datetime').last()
            options.update(report_datetime=household_log_entry.report_datetime)
        options.update(initials=options.get('initials', first_name[0] + last_name[0]))
        return mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            first_name=first_name,
            **options)

    def add_enrollment_checklist(self, household_member, **options):
        options.update(
            initials=options.get('initials', household_member.initials),
            gender=options.get('gender', household_member.gender),
            report_datetime=options.get('report_datetime', self.get_utcnow()))
        return mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            **options)

    def make_absent_member(self, household_member, **options):
        """Returns a household member after adding a absent member report."""
        options.update(report_datetime=options.get('report_datetime', self.get_utcnow()))
        mommy.make_recipe('member.absentmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_refused_member(self, household_member, **options):
        """Returns a household member after adding a refused member report."""
        options.update(report_datetime=options.get('report_datetime', self.get_utcnow()))
        mommy.make_recipe('member.refusedmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_undecided_member(self, household_member, **options):
        """Returns a household member after adding a undecided member report."""
        options.update(report_datetime=options.get('report_datetime', self.get_utcnow()))
        mommy.make_recipe('member.undecidedmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_moved_member(self, household_member, **options):
        """Returns a household member after adding a undecided member report."""
        options.update(report_datetime=options.get('report_datetime', self.get_utcnow()))
        mommy.make_recipe('member.movedmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_deceased_member(self, household_member, **options):
        """Returns a household member after adding a deceased member report."""
        options.update(report_datetime=options.get('report_datetime', self.get_utcnow()))
        mommy.make_recipe('member.deceasedmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_htc_member(self, household_member, **options):
        """Returns a household member after adding a HTC member report."""
        options.update(report_datetime=options.get('report_datetime', self.get_utcnow()))
        mommy.make_recipe('member.htcmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)
