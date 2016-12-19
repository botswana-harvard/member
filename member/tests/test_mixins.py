from model_mommy import mommy

from edc_base.test_mixins import AddVisitMixin, ReferenceDateMixin, CompleteCrfsMixin, LoadListDataMixin

from member.list_data import list_data
from household.tests.test_mixins import HouseholdMixin


class MemberTestMixin(HouseholdMixin, LoadListDataMixin):

    list_data = list_data


class MemberMixin(MemberTestMixin):

    def setUp(self):
        super(MemberMixin, self).setUp()
        self.study_site = '40'

    def make_household_ready_for_enumeration(self):
        """Returns household_structure after adding representative eligibility."""
        household_structure = super().make_household_ready_for_enumeration()
        # add representative eligibility
        mommy.make_recipe(
            'member.representativeeligibility',
            household_structure=household_structure)
        return household_structure

    def add_household_member(self, household_structure, **options):
        """Returns a household member that is by default eligible."""
        return mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure, **options)

    def add_head_of_household_member(self, **options):
        mommy.make_recipe(
            'member.household_member',
            **options)

    def add_household_members(self, member_count=None):
        member_count = member_count or 5
        self.add_head_of_household_member()
        for _ in range(1, member_count):
            self.add_household_member()

    def make_positive_member(self, **options):
        """Make a POS mother LMP 25wks with POS result with evidence (no recent or rapid test)."""
        self.make_new_consented_member()
        report_datetime = options.get('report_datetime', self.test_mixin_reference_datetime)

    def make_negative_member(self, **options):
        """Make a NEG mother LMP 25wks with NEG by current, recent or rapid."""
        self.make_new_consented_member()
        report_datetime = options.get('report_datetime', self.test_mixin_reference_datetime)