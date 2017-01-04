from household.models import HouseholdStructure

from ..models import HouseholdMember


from django.contrib import admin
from django.urls.base import reverse
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_base.modeladmin_mixins import (
    ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin, ModelAdminFormAutoNumberMixin,
    ModelAdminReadOnlyMixin, ModelAdminAuditFieldsMixin, ModelAdminInstitutionMixin)


class HouseholdMemberAdminMixin:

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "household_structure":
            if request.GET.get('household_structure'):
                kwargs["queryset"] = HouseholdStructure.objects.filter(
                    id__exact=request.GET.get('household_structure', 0))
        if db_field.name == "household_member":
            if request.GET.get('household_member'):
                kwargs["queryset"] = HouseholdMember.objects.filter(
                    id__exact=request.GET.get('household_member', 0))
        return super(HouseholdMemberAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def view_on_site(self, obj):
        try:
            household_identifier = obj.household_member.household_structure.household.household_identifier
        except AttributeError:
            household_identifier = obj.household_structure.household.household_identifier
        try:
            survey = obj.household_member.household_structure.survey
        except AttributeError:
            survey = obj.household_structure.survey
        return reverse(
            'enumeration:dashboard_url', kwargs=dict(
                household_identifier=household_identifier,
                survey=survey))


class ModelAdminMixin(ModelAdminInstitutionMixin, ModelAdminFormInstructionsMixin, ModelAdminNextUrlRedirectMixin,
                      ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin, ModelAdminAuditFieldsMixin,
                      ModelAdminReadOnlyMixin, HouseholdMemberAdminMixin, admin.ModelAdmin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'
