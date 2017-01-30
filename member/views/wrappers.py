from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from edc_dashboard.wrappers import ModelWrapper

from ..models import (
    AbsentMember, UndecidedMember, RefusedMember,
    DeceasedMember, EnrollmentChecklist)

app_config = django_apps.get_app_config('member')


class HouseholdFormsModelWrapperMixin(ModelWrapper):
    """For models with a FK to household_structure.
    """
    next_url_name = django_apps.get_app_config(
        'enumeration').dashboard_url_name
    url_instance_attrs = [
        'household_identifier', 'survey_schedule', 'household_structure']

    @property
    def household_structure(self):
        return self._original_object.household_structure

    @property
    def household_identifier(self):
        return (self._original_object.household_structure.
                household.household_identifier)

    @property
    def survey_schedule(self):
        return (self._original_object.household_structure.
                survey_schedule_object.field_value)

    @property
    def survey_schedule_object(self):
        return (self._original_object.household_structure.
                survey_schedule_object)


class MemberStatusModelWrapperMixin(ModelWrapper):

    """For models with a FK to household member."""

    next_url_name = django_apps.get_app_config(
        'enumeration').dashboard_url_name
    url_instance_attrs = [
        'household_identifier', 'survey_schedule', 'household_member']

    @property
    def household_member(self):
        return str(self._original_object.household_member.id)

    @property
    def household_identifier(self):
        return (self._original_object.household_member.
                household_structure.household.household_identifier)

    @property
    def survey_schedule(self):
        return (self._original_object.household_member.
                household_structure.survey_schedule_object.field_value)

    @property
    def survey_schedule_object(self):
        return (self._original_object.household_member.
                household_structure.survey_schedule_object)


class AbsentMemberModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.absentmember'
    extra_querystring_attrs = {
        'member.absentmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {
        'member.absentmember': ['household_identifier', 'survey_schedule']}


class UndecidedMemberModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.undecidedmember'
    extra_querystring_attrs = {
        'member.undecidedmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {
        'member.undecidedmember': ['household_identifier', 'survey_schedule']}


class RefusedMemberModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.refusedmember'
    extra_querystring_attrs = {
        'member.refusedmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {
        'member.refusedmember': ['household_identifier', 'survey_schedule']}


class DeceasedMemberModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.deceasedmember'
    extra_querystring_attrs = {
        'member.deceasedmember': ['survey_schedule', 'household_member']}
    next_url_attrs = {
        'member.deceasedmember': ['household_identifier', 'survey_schedule']}


class EnrollmentChecklistModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.enrollmentchecklist'
    extra_querystring_attrs = {
        'member.enrollmentchecklist': ['survey_schedule', 'household_member']}
    next_url_attrs = {
        'member.enrollmentchecklist': ['household_identifier', 'survey_schedule']}


class EnrollmentChecklistAnonymousModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.enrollmentchecklistanonymous'
    extra_querystring_attrs = {
        'member.enrollmentchecklistanonymous': ['survey_schedule', 'household_member']}
    next_url_attrs = {
        'member.enrollmentchecklistanonymous': ['household_identifier', 'survey_schedule']}
    next_url_name = django_apps.get_app_config(
        'enumeration').anonymous_dashboard_url_name


class HeadOfHouseholdEligibilityModelWrapper(MemberStatusModelWrapperMixin):

    model_name = 'member.householdheadeligibility'
    extra_querystring_attrs = {
        'member.householdheadeligibility': ['survey_schedule', 'household_member']}
    next_url_attrs = {
        'member.householdheadeligibility': ['household_identifier', 'survey_schedule']}


class RepresentativeEligibilityModelWrapper(HouseholdFormsModelWrapperMixin):

    model_name = 'member.representativeeligibility'
    extra_querystring_attrs = {
        'member.representativeeligibility': ['survey_schedule', 'household_structure']}
    next_url_attrs = {
        'member.representativeeligibility': ['household_identifier', 'survey_schedule']}


class HouseholdInfoModelWrapper(HouseholdFormsModelWrapperMixin):

    model_name = 'member.householdinfo'
    extra_querystring_attrs = {
        'member.householdinfo': ['survey_schedule', 'household_structure']}
    next_url_attrs = {
        'member.householdinfo': ['household_identifier', 'survey_schedule']}


class HouseholdMemberModelWrapper(ModelWrapper):

    model_name = 'member.householdmember'
    next_url_name = app_config.listboard_url_name
    extra_querystring_attrs = {
        'member.householdmember': [
            'household_structure',
            'internal_identifier']}
    next_url_attrs = {
        'member.householdmember': [
            'household_identifier',
            'survey_schedule']}
    url_instance_attrs = [
        'household_identifier',
        'survey_schedule',
        'household_structure',
        'internal_identifier']

    @property
    def household_identifier(self):
        return self._original_object.household_structure.household.household_identifier

    @property
    def survey_schedule(self):
        return self._original_object.household_structure.survey_schedule_object.field_value

    @property
    def survey_schedule_object(self):
        return self._original_object.household_structure.survey_schedule_object

    @property
    def plot_identifier(self):
        return self._original_object.household_structure.household.plot.plot_identifier

    @property
    def community_name(self):
        return ' '.join(
            self._original_object.household_structure.household.plot.map_area.split('_'))

    @property
    def absent_members(self):
        return (AbsentMemberModelWrapper(obj)
                for obj in self.wrapped_object.absentmember_set.all())

    @property
    def new_absent_member(self):
        return AbsentMemberModelWrapper(
            AbsentMember(household_member=self._original_object))

    @property
    def undecided_members(self):
        return (UndecidedMemberModelWrapper(obj)
                for obj in self.wrapped_object.undecidedmember_set.all())

    @property
    def new_undecided_member(self):
        return UndecidedMemberModelWrapper(
            UndecidedMember(household_member=self._original_object))

    @property
    def refused_member(self):
        try:
            return RefusedMemberModelWrapper(self.wrapped_object.refusedmember)
        except ObjectDoesNotExist:
            return RefusedMemberModelWrapper(
                RefusedMember(household_member=self._original_object))

    @property
    def deceased_member(self):
        try:
            return DeceasedMemberModelWrapper(self.wrapped_object.deceasedmember)
        except ObjectDoesNotExist:
            return DeceasedMemberModelWrapper(
                DeceasedMember(household_member=self._original_object))

    @property
    def enrollment_checklist(self):
        try:
            return EnrollmentChecklistModelWrapper(self.wrapped_object.enrollmentchecklist)
        except ObjectDoesNotExist:
            return EnrollmentChecklistModelWrapper(
                EnrollmentChecklist(household_member=self._original_object))
