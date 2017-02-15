from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple
from survey.admin import survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import EnrollmentChecklistAnonymousForm
from ..models import EnrollmentChecklistAnonymous, HouseholdMember
from .modeladmin_mixins import ModelAdminMixin


@admin.register(EnrollmentChecklistAnonymous, site=member_admin)
class EnrollmentChecklistAnonymousAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = EnrollmentChecklistAnonymousForm

    date_hierarchy = 'report_datetime'

    instructions = [
        'This form is a tool to assist the Interviewer to confirm the '
        'Eligibility status of the ANONYMOUS subject. '
        'After entering the required items, click SAVE.']

    fieldsets = (
        (None, {
            'fields': (
                'household_member',
                'report_datetime',
                'citizen',
                'gender',
                'age_in_years',
                "guardian",
                "literacy",
                "study_participation",
                "part_time_resident",
                'may_store_samples',)
        }),
        ('Review', {
            'fields': (
                'consent_reviewed',
                'study_questions',
                'assessment_score')
        }),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = ('household_member', 'report_datetime',
                    'gender', 'age_in_years', 'may_store_samples', )

    list_filter = (
        'report_datetime',
        'gender', 'is_eligible', 'may_store_samples')

    radio_fields = {
        "citizen": admin.VERTICAL,
        "gender": admin.VERTICAL,
        "part_time_resident": admin.VERTICAL,
        "literacy": admin.VERTICAL,
        "guardian": admin.VERTICAL,
        "study_participation": admin.VERTICAL,
        "may_store_samples": admin.VERTICAL,
        "consent_reviewed": admin.VERTICAL,
        "study_questions": admin.VERTICAL,
        "assessment_score": admin.VERTICAL,
    }

    search_fields = (
        'household_member__subject_identifier', 'household_member__pk')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "household_member":
            kwargs["queryset"] = HouseholdMember.objects.filter(
                id__exact=request.GET.get('household_member', None))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def view_on_site(self, obj):
        return None
