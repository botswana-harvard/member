from django.apps import apps as django_apps

from household.views import HouseholdAppConfigViewMixin

from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember

from .wrappers import HouseholdMemberModelWrapper
from django.core.exceptions import ObjectDoesNotExist


class MemberAppConfigViewMixin(HouseholdAppConfigViewMixin):

    app_config_name = 'member'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            bcpp_subject_listboard_url_name=django_apps.get_app_config('bcpp_subject').listboard_url_name,
        )
        return context


class HouseholdMemberViewMixin:

    household_member_wrapper_class = HouseholdMemberModelWrapper

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.household_member = None
        self.household_members = None
        self.head_of_household = None

    def get(self, request, *args, **kwargs):
        """Add household member to the instance."""
        try:
            household_member = HouseholdMember.objects.get(
                subject_identifier=self.subject_identifier,
                household_structure__id=self.household_structure.id)  # use id, model is wrapped
        except HouseholdMember.DoesNotExist:
            self.household_member = None
        else:
            self.household_member = self.household_member_wrapper_class(household_member)

        household_members = self.household_structure.wrapped_object.householdmember_set.all().order_by('first_name')
        self.household_members = (self.household_member_wrapper_class(obj) for obj in household_members)
        try:
            self.head_of_household = (
                self.household_structure.wrapped_object.householdmember_set.get(
                    relation=HEAD_OF_HOUSEHOLD))
        except ObjectDoesNotExist:
            self.head_of_household = None

        kwargs['household_member'] = self.household_member
        kwargs['household_members'] = self.household_members
        return super().get(request, *args, **kwargs)
