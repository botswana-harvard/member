from django.contrib import admin

from ..admin_site import bcpp_household_admin
from ..forms import HouseholdLogForm, HouseholdLogEntryForm
from ..models import HouseholdLogEntry, HouseholdLog

from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdLogEntry, site=bcpp_household_admin)
class HouseholdLogEntryAdmin(ModelAdminMixin):
    form = HouseholdLogEntryForm
    date_hierarchy = 'modified'
    list_per_page = 15
    fields = ('household_log', 'report_datetime', 'household_status',
              'next_appt_datetime', 'next_appt_datetime_source', 'comment')
    list_display = ('household_log', 'report_datetime', 'next_appt_datetime')
    list_filter = ('household_log__household_structure__survey', 'report_datetime',
                   'next_appt_datetime', 'household_log__household_structure__household__community')
    radio_fields = {
        "next_appt_datetime_source": admin.VERTICAL,
        "household_status": admin.VERTICAL,
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "household_log":
            if request.GET.get('household_log'):
                kwargs["queryset"] = HouseholdLog.objects.filter(id__exact=request.GET.get('household_log', 0))
            else:
                self.readonly_fields = list(self.readonly_fields)
                try:
                    self.readonly_fields.index('household_log')
                except ValueError:
                    self.readonly_fields.append('household_log')
        return super(HouseholdLogEntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class HouseholdLogEntryInline(admin.TabularInline):
    model = HouseholdLogEntry
    extra = 0
    max_num = 5


@admin.register(HouseholdLog, site=bcpp_household_admin)
class HouseholdLogAdmin(ModelAdminMixin):
    form = HouseholdLogForm
    instructions = []
    inlines = [HouseholdLogEntryInline, ]
    date_hierarchy = 'modified'
    list_per_page = 15
    list_display = ('household_structure', 'structure', 'modified', 'user_modified', 'hostname_modified')
    readonly_fields = ('household_structure', )
    search_fields = ('household_structure__household__household_identifier', 'household_structure__pk')
    list_filter = ('household_structure__survey', 'hostname_created', 'created')
