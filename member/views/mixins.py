from django.core.exceptions import ObjectDoesNotExist

from edc_constants.constants import MALE, FEMALE

from household.models import HouseholdStructure

from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember
from .wrappers import HouseholdMemberModelWrapper


class HouseholdMemberViewMixin:

    household_member_wrapper_class = HouseholdMemberModelWrapper

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._head_of_household = None
        self._household_member = None
        self.household_members = []

    def get(self, request, *args, **kwargs):
        """Add household member(s) to the view.
        """
        household_members = []
        for household_structure in HouseholdStructure.objects.filter(
                household__household_identifier=self.household_identifier):
            household_members.extend(
                [obj for obj in household_structure.householdmember_set.all(
                ).order_by('first_name')])

        for household_member in household_members:
            household_member.editable_in_view = self.member_editable_in_view(
                household_member)
            self.household_members.append(
                self.household_member_wrapper_class(household_member))

        kwargs['household_member'] = self.household_member
        kwargs['head_of_household'] = self.head_of_household
        kwargs['household_members'] = self.household_members
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            MALE=MALE,
            FEMALE=FEMALE)
        return context

    def member_editable_in_view(self, household_member):
        """Returns True if member instance and its related data
        may be edited in the view."""
        if (household_member.survey_schedule_object.field_value ==
                self.survey_schedule_object.field_value):
            editable_in_view = True
        else:
            editable_in_view = False
        if not self.current_household_log_entry.id:
            editable_in_view = False
        return editable_in_view

    @property
    def household_member(self):
        """Returns a wrapped model, either saved or not.
        """
        if not self._household_member:
            try:
                household_member = HouseholdMember.objects.get(
                    subject_identifier=self.subject_identifier,
                    household_structure__id=self.household_structure.id)
            except HouseholdMember.DoesNotExist:
                household_member = HouseholdMember(
                    household_structure=self.household_structure._original_object,
                    survey_schedule=(self.household_structure._original_object.
                                     survey_schedule_object.field_value))
            self._household_member = self.household_member_wrapper_class(
                household_member)
        return self._household_member

    @property
    def head_of_household(self):
        """Returns a wrapped model, either saved or not.
        """
        if not self._head_of_household:
            try:
                head_of_household = (
                    self.household_structure.wrapped_object.householdmember_set.get(
                        relation=HEAD_OF_HOUSEHOLD))
            except ObjectDoesNotExist:
                head_of_household = HouseholdMember(
                    household_structure=self.household_structure._original_object)
            self._head_of_household = self.household_member_wrapper_class(
                head_of_household)
        return self._head_of_household
