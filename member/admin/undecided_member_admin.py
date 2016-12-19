from django.contrib import admin

from ..admin_site import member_admin
from ..forms import UndecidedMemberForm
from ..models import UndecidedMember

from .modeladmin_mixins import HouseholdMemberAdminMixin
from .undecided_member_entry_admin import UndecidedMemberEntryInline


@admin.register(UndecidedMember, site=member_admin)
class UndecidedMemberAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    instructions = []

    form = UndecidedMemberForm
    inlines = [UndecidedMemberEntryInline, ]

    dashboard_type = 'subject'

    subject_identifier_attribute = 'registration_identifier'

    fields = (
        'household_member',
        'report_datetime')

    list_display = (
        'household_member',
        'report_datetime')

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey',
        'household_member__household_structure__household__plot__map_area')

    search_fields = [
        'household_member__first_name',
        'household_member__household_structure__household__household_identifier', ]
