from dateutil.relativedelta import relativedelta
from faker import Faker
from model_mommy import mommy

from edc_base_test.exceptions import TestMixinError
from edc_base_test.mixins import LoadListDataMixin
from edc_constants.constants import MALE

from household.models import HouseholdStructure
from household.tests.test_mixins import HouseholdMixin

from ..constants import HEAD_OF_HOUSEHOLD
from ..list_data import list_data
from ..models import HouseholdMember
from ..models.household_member.utils import clone_members


fake = Faker()


class MemberTestMixin(HouseholdMixin, LoadListDataMixin):

    list_data = list_data


class MemberMixin(MemberTestMixin):

    def setUp(self):
        super(MemberMixin, self).setUp()
        self.study_site = '40'

    def _make_ready(self, household_structure, make_hoh=None, **options):
        """Returns household_structure after adding representative eligibility.

        For internal use."""
        make_hoh = True if make_hoh is None else make_hoh

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
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        return household_structure

    def make_household_ready_for_enumeration(self, make_hoh=None, **options):
        """Returns household_structure after adding representative eligibility.

        By default the household_structure is that of the first survey_schedule."""
        options.update(attempts=options.get('attempts', 1))
        household_structure = self.make_household_structure(**options)
        return self._make_ready(household_structure, make_hoh=make_hoh, **options)

    def make_household_ready_for_next(self, household_structure, make_hoh=None, **options):
        """Returns the `household_structure` for the next survey.

        Same as `make_household_ready_for_enumeration` except uses the given
        `household_structure`.
        """
        options.update(attempts=options.get('attempts', 1))
        survey_schedule = household_structure.survey_schedule_object.next
        if survey_schedule:
            return self._make_ready(household_structure, make_hoh=make_hoh, **options)
        return None

    def make_household_ready_for_last(self, household_structure, make_hoh=None, **options):
        """Returns the `household_structure` for the next survey.

        Same as `make_household_ready_for_enumeration` except uses the given
        `household_structure`.
        """
        options.update(attempts=options.get('attempts', 1))
        survey_schedule = household_structure.survey_schedule_object.last
        return self._make_ready(
            household_structure, survey_schedule=survey_schedule, make_hoh=make_hoh, **options)

    def make_ahs_household_member(self, bhs_consented_household_member, survey_schedule):
        """Return a ahs household structure."""
        household_structure = HouseholdStructure.objects.get(
            household=bhs_consented_household_member.household_structure.household,
            survey_schedule=survey_schedule.field_value)
        household_log_entry = self.make_household_log_entry(
            household_log=household_structure.householdlog,
            report_datetime=self.get_utcnow())
        mommy.make_recipe(
            'member.representativeeligibility',
            report_datetime=household_log_entry.report_datetime,
            household_structure=household_structure)
        household_structure = HouseholdStructure.objects.get(
            id=household_structure.id)
        member = clone_members(
            household_structure=household_structure,
            report_datetime=self.get_utcnow())[0]
        member.save()
        return member

    def make_enumerated_household_with_male_member(self, survey_schedule=None):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=True, survey_schedule=survey_schedule, gender=MALE)
        return household_structure

    def add_household_member(self, household_structure, **options):
        """Returns a household member that is by default eligible."""

        first_name = fake.first_name()
        last_name = fake.last_name()
        options.update(first_name=options.get('first_name', first_name))
        options.update(
            initials=options.get('initials', first_name[0] + last_name[0]))

        if not options.get('report_datetime'):
            last = household_structure.householdlog.householdlogentry_set.all().order_by(
                'report_datetime').last()
            options.update(report_datetime=last.report_datetime)

        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            **options)

        if not options and not household_member.eligible_member:
            raise TestMixinError(
                'Default values expected to create an eligible household member. '
                'Got eligible_member=False. Did someone mess with the mommy recipe?')
        return household_member

    def add_enrollment_checklist(self, household_member, **options):
        """Returns a new enrollment_checklistt."""
        report_datetime = options.get('report_datetime', self.get_utcnow())
        if 'age_in_years' in options:
            raise TestMixinError('Invalid option. Got \'age_in_years\'')
        options.update(
            initials=options.get('initials', household_member.initials),
            gender=options.get('gender', household_member.gender),
            dob=options.get('dob', (report_datetime - relativedelta(
                years=household_member.age_in_years)).date()))
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
