from model_mommy import mommy

from edc_base.test_mixins import LoadListDataMixin

from member.list_data import list_data
from household.tests.test_mixins import HouseholdMixin
from member.constants import HEAD_OF_HOUSEHOLD
from member.models.household_member import HouseholdMember


class MemberTestMixin(HouseholdMixin, LoadListDataMixin):

    list_data = list_data


class MemberMixin(MemberTestMixin):
    consent_model = 'edc_example.subjectconsent'

    def setUp(self):
        super(MemberMixin, self).setUp()
        self.study_site = '40'

    def make_household_ready_for_enumeration(self, make_hod=None):
        """Returns household_structure after adding representative eligibility."""
        make_hod = True if make_hod is None else make_hod
        household_structure = super().make_household_ready_for_enumeration()
        # add representative eligibility
        mommy.make_recipe(
            'member.representativeeligibility',
            household_structure=household_structure)
        if make_hod:
            household_member = mommy.make_recipe(
                'member.householdmember',
                household_structure=household_structure,
                relation=HEAD_OF_HOUSEHOLD)
            mommy.make_recipe(
                'member.householdheadeligibility',
                household_member=household_member)
        return household_structure

    def add_household_member(self, household_structure, **options):
        """Returns a household member that is by default eligible."""
        return mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            **options)

    def add_enrollment_checklist(self, household_member, **options):
        return mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            **options)

    def make_absent_member(self, household_member, **options):
        """Returns a household member after adding a absent member report."""
        mommy.make_recipe('member.absentmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_refused_member(self, household_member, **options):
        """Returns a household member after adding a refused member report."""
        mommy.make_recipe('member.refusedmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_undecided_member(self, household_member, **options):
        """Returns a household member after adding a undecided member report."""
        mommy.make_recipe('member.undecidedmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_deceased_member(self, household_member, **options):
        """Returns a household member after adding a deceased member report."""
        mommy.make_recipe('member.deceasedmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_htc_member(self, household_member, **options):
        """Returns a household member after adding a HTC member report."""
        mommy.make_recipe('member.htcmember', household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)
