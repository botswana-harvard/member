from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple
from survey.admin import survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import DeceasedMemberForm
from ..models import DeceasedMember
from .modeladmin_mixins import ModelAdminMixin


@admin.register(DeceasedMember, site=member_admin)
class DeceasedMemberAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = DeceasedMemberForm

    fieldsets = (
        (None, {
            'fields': (
                'household_member',
                'report_datetime',
                'death_date',
                'site_aware_date',
                'death_cause',
                'duration_of_illness',
                'relationship_death_study',
                'extra_death_info',
                'extra_death_info_date')}),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = ('household_member', 'report_datetime')

    search_fields = [
        'household_member__first_name',
        'household_member__subject_identifier',
        'household_member__household_structure__household__household_identifier']

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey_schedule',
        'household_member__household_structure__household__plot__map_area')

    radio_fields = {'relationship_death_study': admin.VERTICAL}
