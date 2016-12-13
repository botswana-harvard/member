from django.contrib import admin

from ..admin_site import member_admin
from ..models import AbsentMember, AbsentMemberEntry

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(AbsentMemberEntry, site=member_admin)
class AbsentMemberEntryAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    fields = (
        'absent_member',
        'report_datetime',
        'next_appt_datetime',
        'next_appt_datetime_source',
        'reason',
        'reason_other',
        'contact_details')

    list_display = (
        'absent_member',
        'report_datetime',
        'next_appt_datetime',
        'contact_details')

    radio_fields = {
        "reason": admin.VERTICAL,
        "next_appt_datetime_source": admin.VERTICAL}

    list_filter = (
        'report_datetime',
        'absent_member__household_member__household_structure__survey__survey_slug',
        'absent_member__household_member__household_structure__household__plot__community')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "absent_member":
            kwargs["queryset"] = AbsentMember.objects.filter(id__exact=request.GET.get('absent_member', 0))
        return super(AbsentMemberEntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
