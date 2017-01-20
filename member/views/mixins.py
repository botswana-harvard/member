from django.core.exceptions import ObjectDoesNotExist

from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember

from .wrappers import HouseholdMemberModelWrapper


class HouseholdMemberViewMixin:

    household_member_wrapper_class = HouseholdMemberModelWrapper

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._head_of_household = None
        self._household_member = None
        self.household_members = None

    def get(self, request, *args, **kwargs):
        """Add household member(s) to the instance."""

        household_members = self.household_structure.wrapped_object.householdmember_set.all().order_by('first_name')
        self.household_members = (self.household_member_wrapper_class(obj) for obj in household_members)

        kwargs['household_member'] = self.household_member
        kwargs['head_of_household'] = self.head_of_household
        kwargs['household_members'] = self.household_members
        return super().get(request, *args, **kwargs)

    @property
    def household_member(self):
        """Returns a wrapped model, either saved or not."""
        if not self._household_member:
            try:
                household_member = HouseholdMember.objects.get(
                    subject_identifier=self.subject_identifier,
                    household_structure__id=self.household_structure.id)
            except HouseholdMember.DoesNotExist:
                household_member = HouseholdMember(
                    household_structure=self.household_structure._original_object)
            self._household_member = self.household_member_wrapper_class(household_member)
        return self._household_member

    @property
    def head_of_household(self):
        """Returns a wrapped model, either saved or not."""
        if not self._head_of_household:
            try:
                head_of_household = (
                    self.household_structure.wrapped_object.householdmember_set.get(
                        relation=HEAD_OF_HOUSEHOLD))
            except ObjectDoesNotExist:
                head_of_household = HouseholdMember(
                    household_structure=self.household_structure._original_object)
            self._head_of_household = self.household_member_wrapper_class(head_of_household)
        return self._head_of_household
