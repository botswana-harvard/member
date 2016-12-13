from django.contrib import admin


from ..admin_site import member_admin
from ..forms import EnrollmentChecklistForm
from ..models import EnrollmentChecklist

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(EnrollmentChecklist, site=member_admin)
class EnrollmentChecklistAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    form = EnrollmentChecklistForm

    date_hierarchy = 'report_datetime'

    instructions = ['This form is a tool to assist the Interviewer to confirm the '
                    'Eligibility status of the subject. After entering the required items, click SAVE.']

    fields = (
        'household_member',
        'report_datetime',
        'initials',
        'dob',
        'gender',
        'has_identity',
        "citizen",
        "legal_marriage",
        "study_participation",
        "confirm_participation",
        "marriage_certificate",
        "part_time_resident",
        "household_residency",
        "literacy",
        "guardian",
    )

    list_display = ('household_member', 'report_datetime', 'gender', 'is_eligible', )

    list_filter = (
        'report_datetime',
        'gender', 'is_eligible',
        'household_member__household_structure__survey__survey_slug',
        'household_member__household_structure__household__plot__community')

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
