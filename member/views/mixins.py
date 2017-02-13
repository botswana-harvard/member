from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from edc_constants.constants import MALE, FEMALE

from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember
from .wrappers import HouseholdMemberModelWrapper


class HouseholdMemberViewMixin:

    household_member_model_wrapper_class = HouseholdMemberModelWrapper

    def get_context_data(self, **kwargs):
        """Add household member(s) to the context.
        """
        context = super().get_context_data(**kwargs)
        print('HouseholdMemberViewMixin')
        context.update(
            household_member=self.household_member_wrapped,
            head_of_household=self.head_of_household_wrapped,
            household_members=self.household_members_wrapped,
            MALE=MALE,
            FEMALE=FEMALE)
        return context

    @property
    def household_member(self):
        """Returns a household member model instance or None.
        """
        try:
            household_member = HouseholdMember.objects.get(
                subject_identifier=self.subject_identifier,
                household_structure=self.household_structure)
        except HouseholdMember.DoesNotExist:
            household_member = None
        return household_member

    @property
    def household_member_wrapped(self):
        """Returns a wrapped household member or None.
        """
        if self.household_member:
            return self.household_member_model_wrapper_class(self.household_member)
        return None
#         obj = (
#             self.household_member
#             or HouseholdMember(
#                 household_structure=self.household_structure,
#                 survey_schedule=(
#                     self.household_structure
#                     .survey_schedule_object.field_value)))
#         return self.household_member_model_wrapper_class(obj)

    @property
    def head_of_household(self):
        """Returns a household member model instance (HoH) or None.

        If more than one exists, returns first
        """
        try:
            head_of_household = (
                self.household_structure.householdmember_set.get(
                    relation=HEAD_OF_HOUSEHOLD))
        except ObjectDoesNotExist:
            head_of_household = None
        except MultipleObjectsReturned:
            head_of_household = (
                self.household_structure.householdmember_set.filter(
                    relation=HEAD_OF_HOUSEHOLD).first())
        except AttributeError as e:
            if 'householdmember_set' not in str(e):
                raise
            head_of_household = None
        return head_of_household

    @property
    def head_of_household_wrapped(self):
        """Returns a wrapped household member (HoH) or None.
        """
        if self.head_of_household:
            return self.household_member_model_wrapper_class(
                self.head_of_household)
        return None

    @property
    def household_members(self):
        """Returns a Queryset of household members for this household.
        """
        return (HouseholdMember.objects.filter(
            household_structure__household__household_identifier=self.household_identifier)
            .order_by('first_name'))

    @property
    def household_members_wrapped(self):
        """Returns a list of wrapped household members for this household.
        """
        wrapped_objects = []
        for obj in self.household_members:
            obj.editable_in_view = self.member_editable_in_view(obj)
            wrapped_objects.append(
                self.household_member_model_wrapper_class(obj))
        return wrapped_objects

    def member_editable_in_view(self, household_member):
        """Returns True if household member model instance and
        its related data may be edited in the view.

        Criteria: (1) must be in the current survey schedule,
            (2) have a current household log entry.
        """
        if (household_member.survey_schedule_object.field_value ==
                self.survey_schedule_object.field_value):
            editable_in_view = True
        else:
            editable_in_view = False
        if not self.current_household_log_entry:
            editable_in_view = False
        return editable_in_view
