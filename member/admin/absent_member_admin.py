from django.contrib import admin

from edc_base.modeladmin_mixins import TabularInlineMixin

from ..admin_site import member_admin
from ..forms import AbsentMemberEntryForm
from ..models import AbsentMember, AbsentMemberEntry

from .modeladmin_mixins import ModelAdminMixin


class AbsentMemberEntryInline(TabularInlineMixin, admin.TabularInline):
    fields = (
        'household_member',
        'report_datetime',
        'reason',
        'reason_other',
        'next_appt_datetime',
        'next_appt_datetime_source',)
    form = AbsentMemberEntryForm
    model = AbsentMemberEntry
    max_num = 3
    extra = 1


@admin.register(AbsentMember, site=member_admin)
class AbsentMemberAdmin(ModelAdminMixin):

    form = AbsentMemberEntryForm
    inlines = [AbsentMemberEntryInline, ]

    dashboard_type = 'subject'

    subject_identifier_attribute = 'registration_identifier'

    search_fields = ['household_member__first_name',
                     'household_member__household_structure__household__household_identifier', ]
    list_display = ['household_member', 'report_datetime']
    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey',
        'household_member__household_structure__household__plot__map_area')

    fields = (
        'household_member',
        'report_datetime')

    readonly_fields = (
        'household_member',
        'report_datetime',)
    instructions = []
