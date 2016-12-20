from django.contrib import admin

from ..admin_site import member_admin
from ..forms import UndecidedMemberForm
from ..models import UndecidedMember

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(UndecidedMember, site=member_admin)
class UndecidedMemberAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    form = UndecidedMemberForm

    fields = (
        'household_member',
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

    list_filter = ('report_datetime', )
