from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple
from survey.admin import survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import EnrollmentChecklistForm
from ..models import EnrollmentChecklist

from .modeladmin_mixins import ModelAdminMixin


@admin.register(EnrollmentChecklist, site=member_admin)
class EnrollmentChecklistAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = EnrollmentChecklistForm

    date_hierarchy = 'report_datetime'

    instructions = [
        'This form is a tool to assist the Interviewer to confirm the '
        'Eligibility status of the subject. After entering the required '
        'items, click SAVE.']

    fieldsets = (
        (None, {
            'fields': (
                'household_member',
                'report_datetime',
                'gender',
                "citizen",
                "legal_marriage",
                "study_participation",
                "confirm_participation",
                "marriage_certificate",
                "part_time_resident",
                "household_residency",
                "literacy",
                "guardian",
            )}),
        ('Citizen or legally married to citizen', {
            'fields': (
                'initials',
                'dob',
                'has_identity')}),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = (
        'household_member', 'report_datetime', 'gender', 'is_eligible', )

    list_filter = (
        'report_datetime',
        'gender', 'is_eligible',
        'household_member__household_structure__survey_schedule',
        'household_member__household_structure__household__plot__map_area')

    radio_fields = {
        'has_identity': admin.VERTICAL,
        "gender": admin.VERTICAL,
        "citizen": admin.VERTICAL,
        "legal_marriage": admin.VERTICAL,
        "marriage_certificate": admin.VERTICAL,
        "part_time_resident": admin.VERTICAL,
        "household_residency": admin.VERTICAL,
        "literacy": admin.VERTICAL,
        "guardian": admin.VERTICAL,
        "study_participation": admin.VERTICAL,
        "confirm_participation": admin.VERTICAL,
    }

    search_fields = ('household_member__first_name', 'household_member__pk')
