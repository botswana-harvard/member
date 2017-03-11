from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple
from survey.admin import survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import UndecidedMemberForm
from ..models import UndecidedMember
from .modeladmin_mixins import ModelAdminMixin


@admin.register(UndecidedMember, site=member_admin)
class UndecidedMemberAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = UndecidedMemberForm

    fieldsets = (
        (None, {
            'fields': (
                'household_member',
                'report_datetime',
                'next_appt_datetime',
                'next_appt_datetime_source',
                'reason',
                'reason_other',
                'contact_details')}),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = (
        'household_member',
        'report_datetime',
        'next_appt_datetime',
        'contact_details')

    radio_fields = {
        "reason": admin.VERTICAL,
        "next_appt_datetime_source": admin.VERTICAL}

    list_filter = ('report_datetime', )
