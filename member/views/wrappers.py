from django.apps import apps as django_apps

from edc_dashboard.wrappers import ModelWrapper
from django.core.exceptions import ObjectDoesNotExist

app_config = django_apps.get_app_config('member')


class MemberStatusModelWrapperMixin(ModelWrapper):

    model_name = 'member.absentmember'
    admin_site_name = app_config.admin_site_name
    url_namespace = app_config.url_namespace
    next_url_name = django_apps.get_app_config('enumeration').dashboard_url_name
    extra_querystring_attrs = {'member.absentmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {'member.absentmember': ['household_identifier', 'survey_schedule']}
    url_instance_attrs = ['household_identifier', 'survey_schedule', 'household_member']

    @property
    def household_identifier(self):
        return self._original_object.household_member.household_structure.household.household_identifier

    @property
    def survey_schedule(self):
        return self._original_object.household_member.survey_schedule_object.field_value

    @property
    def survey_schedule_object(self):
        return self._original_object.household_member.survey_schedule_object


class AbsentMemberModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.absentmember'
    extra_querystring_attrs = {'member.absentmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {'member.absentmember': ['household_identifier', 'survey_schedule']}


class UndecidedMemberModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.undecidedmember'
    extra_querystring_attrs = {'member.undecidedmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {'member.undecidedmember': ['household_identifier', 'survey_schedule']}


class RefusedMemberModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.refusedmember'
    extra_querystring_attrs = {'member.refusedmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {'member.refusedmember': ['household_identifier', 'survey_schedule']}


class DeceasedMemberModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.deceasedmember'
    extra_querystring_attrs = {'member.deceasedmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {'member.deceasedmember': ['household_identifier', 'survey_schedule']}


class HouseholdMemberModelWrapper(ModelWrapper):

    model_name = 'member.householdmember'
    admin_site_name = app_config.admin_site_name
    url_namespace = app_config.url_namespace
    next_url_name = app_config.listboard_url_name
    extra_querystring_attrs = {'member.householdmember': ['survey_schedule', 'household_structure']}
    next_url_attrs = {'member.householdmember': ['household_identifier', 'survey_schedule']}
    url_instance_attrs = ['household_identifier', 'survey_schedule', 'household_structure']

    @property
    def household_identifier(self):
        return self._original_object.household_structure.household.household_identifier

    @property
    def survey_schedule(self):
        return self.survey_schedule_object.field_value

    @property
    def survey_schedule_object(self):
        return self._original_object.household_structure.survey_schedule_object

    @property
    def plot_identifier(self):
        return self._original_object.household_structure.household.plot.plot_identifier

    @property
    def community_name(self):
        return ' '.join(self._original_object.household_structure.household.plot.map_area.split('_'))

    @property
    def absent_members(self):
        return (AbsentMemberModelWrapper(obj) for obj in self.wrapped_object.absentmember_set.all())

    @property
    def undecided_members(self):
        return (UndecidedMemberModelWrapper(obj) for obj in self.wrapped_object.undecidedmember_set.all())

    @property
    def refused_member(self):
        try:
            return RefusedMemberModelWrapper(self.wrapped_object.refusedmember)
        except ObjectDoesNotExist:
            return None

    @property
    def deceased_member(self):
        try:
            return UndecidedMemberModelWrapper(self.wrapped_object.deceasedmember)
        except ObjectDoesNotExist:
            return None
