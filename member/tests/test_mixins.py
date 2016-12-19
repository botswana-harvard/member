from model_mommy import mommy

from edc_base.test_mixins import LoadListDataMixin

from member.list_data import list_data
from household.tests.test_mixins import HouseholdMixin
from member.constants import HEAD_OF_HOUSEHOLD


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

    def make_positive_member(self, **options):
        """Make a POS mother LMP 25wks with POS result with evidence (no recent or rapid test)."""
        self.make_new_consented_member()
        report_datetime = options.get('report_datetime', self.test_mixin_reference_datetime)

    def make_negative_member(self, **options):
        """Make a NEG mother LMP 25wks with NEG by current, recent or rapid."""
        self.make_new_consented_member()
        report_datetime = options.get('report_datetime', self.test_mixin_reference_datetime)
