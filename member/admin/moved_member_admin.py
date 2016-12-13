from django.contrib import admin

from ..admin_site import member_admin
from ..forms import MovedMemberForm
from ..models import MovedMember

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(MovedMember, site=member_admin)
class MovedMemberAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):
    form = MovedMemberForm
    dashboard_type = 'subject'
    subject_identifier_attribute = 'registration_identifier'

    fields = (
        'household_member',
        'report_datetime',
        'moved_household',
        'moved_community',
        'new_community',
        'update_locator',
        'comment')
    list_display = (
        'household_member',
        'moved_household',
        'moved_community',
        'new_community',
        'update_locator',
    )
    search_fields = [
        'household_member__first_name',
        'household_member__household_structure__household__household_identifier']

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey__survey_slug',
        'household_member__household_structure__household__plot__community')

    radio_fields = {
        "moved_household": admin.VERTICAL,
        "moved_community": admin.VERTICAL,
        "update_locator": admin.VERTICAL,
    }
