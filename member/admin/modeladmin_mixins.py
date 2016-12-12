from django.contrib import admin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_base.modeladmin_mixins import (
    ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin, ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin)
from edc_export.actions import export_as_csv_action

from ..models import Household, HouseholdStructure


class ModelAdminMixin(ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
                      ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin, ModelAdminAuditFieldsMixin,
                      ModelAdminReadOnlyMixin, admin.ModelAdmin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'
    actions = [export_as_csv_action(
        "Export as csv", fields=[], exclude=['id', ]
    )]

    def redirect_url(self, request, obj, post_url_continue=None):
        return request.GET.get('next')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "household_structure":
            if request.GET.get('household_structure'):
                kwargs["queryset"] = HouseholdStructure.objects.filter(
                    id__exact=request.GET.get('household_structure', 0))
            else:
                self.readonly_fields = list(self.readonly_fields)
                try:
                    self.readonly_fields.index('household_structure')
                except ValueError:
                    self.readonly_fields.append('household_structure')
        return super(ModelAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)
