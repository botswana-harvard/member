from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple
from survey.admin import survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import MovedMemberForm
from ..models import MovedMember
from .modeladmin_mixins import ModelAdminMixin


@admin.register(MovedMember, site=member_admin)
class MovedMemberAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = MovedMemberForm

    fieldsets = (
        (None, {
            'fields': (
                'household_member',
                'report_datetime',
                'moved_household',
                'moved_community',
                'new_community',
                'update_locator',
                'comment')}),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = (
        'household_member',
        'moved_household',
        'moved_community',
        'new_community',
        'update_locator',
    )

    search_fields = [
        'household_member__first_name',
        'household_member__subject_identifier',
        'household_member__household_structure__household__household_identifier']

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey_schedule',
        'household_member__household_structure__household__plot__map_area')

    radio_fields = {
        "moved_household": admin.VERTICAL,
        "moved_community": admin.VERTICAL,
        "update_locator": admin.VERTICAL,
    }
