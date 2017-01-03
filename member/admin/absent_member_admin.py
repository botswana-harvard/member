from django.contrib import admin

from ..admin_site import member_admin
from ..models import AbsentMember

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(AbsentMember, site=member_admin)
class AbsentMemberAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    fields = (
        'household_member',
        'report_date',
        'next_appt_datetime',
        'next_appt_datetime_source',
        'reason',
        'reason_other',
        'contact_details')

    list_display = (
        'household_member',
        'report_datetime',
        'next_appt_datetime',
        'contact_details')

    radio_fields = {
        "reason": admin.VERTICAL,
        "next_appt_datetime_source": admin.VERTICAL}

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey',
        'household_member__household_structure__household__plot__map_area')
