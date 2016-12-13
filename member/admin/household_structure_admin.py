from django.contrib import admin

from ..admin_site import member_admin
from ..actions import export_as_kml_hs
from ..forms import HouseholdStructureForm
from ..models import HouseholdStructure, Plot

from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdStructure, site=member_admin)
class HouseholdStructureAdmin(ModelAdminMixin):

    actions = [export_as_kml_hs]

    form = HouseholdStructureForm
    date_hierarchy = 'modified'
    instructions = []
    list_display = (
        'plot',
        'survey',
        'house',
        'enrolled',
        'refused_enumeration',
        'dashboard',
        'members',
        'logs',
        'progress',
        'modified',
        'user_modified',
        'failed_enumeration_attempts')
    list_filter = (
        'survey',
        'progress',
        'enrolled',
        'refused_enumeration',
        'household__community',
        'enrolled_datetime',
        'modified',
        'user_modified',
        'hostname_modified',
        'failed_enumeration_attempts',
    )
    search_fields = (
        'household__household_identifier',
        'household__id',
        'id',)
    radio_fields = {
        'survey': admin.VERTICAL,
    }
    readonly_fields = ('survey', )
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "plot":
            if request.GET.get('plot'):
                kwargs["queryset"] = Plot.objects.filter(
                    id__exact=request.GET.get('plot', 0))
            else:
                self.readonly_fields = list(self.readonly_fields)
                try:
                    self.readonly_fields.index('plot')
                except ValueError:
                    self.readonly_fields.append('plot')
        return super(HouseholdStructureAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
