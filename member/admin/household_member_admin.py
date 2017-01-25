from django.contrib import admin

from edc_base.modeladmin_mixins import TabularInlineMixin, audit_fieldset_tuple

from bcpp.surveys import BCPP_YEAR_2, BCPP_YEAR_3
from survey import S
from survey.admin import survey_schedule_fields, survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import HouseholdMemberForm
from ..models import HouseholdMember

from .modeladmin_mixins import ModelAdminMixin
from edc_base.fieldsets import (
    Fieldset, FieldsetsModelAdminMixin as BaseFieldsetsModelAdminMixin)


class HouseholdMemberInline(TabularInlineMixin, admin.TabularInline):
    model = HouseholdMember
    extra = 3

status_fields = (
    'visit_attempts',
    'eligible_member',
    'eligible_subject',
    'is_consented',
    'enrollment_checklist_completed',
    'enrollment_loss_completed',
    'reported',
    'refused',
    'eligible_htc')

personal_details_fields = (
    'personal_details_changed',
    'details_change_reason')


class FieldsetsModelAdminMixin(BaseFieldsetsModelAdminMixin):

    def get_instance(self, request):
        return None

    def get_key(self, request):
        """Returns the name of the household members previous survey schedule
        or None.

        If key has value, the fieldset will be added to modeladmin.fieldsets.
        """
        key = None
        try:
            household_member = HouseholdMember.objects.get(
                household_structure=request.GET.get('household_structure'),
                survey_schedule=request.GET.get('survey_schedule'))
        except HouseholdMember.DoesNotExist:
            pass
        else:
            previous = household_member.previous
            if previous:
                key = S(previous.survey_schedule).survey_schedule_name
        return key


@admin.register(HouseholdMember, site=member_admin)
class HouseholdMemberAdmin(ModelAdminMixin, FieldsetsModelAdminMixin,
                           admin.ModelAdmin):
    form = HouseholdMemberForm

    list_select_related = ('household_structure', )
    list_per_page = 15

    conditional_fieldsets = {
        BCPP_YEAR_2: Fieldset(
            *personal_details_fields,
            section='Updated Personal Details'),
        BCPP_YEAR_3: Fieldset(
            *personal_details_fields,
            section='Updated Personal Details'),
    }

    fieldsets = (
        (None, {
            'fields': (
                'household_structure',
                'first_name',
                'initials',
                'gender',
                'age_in_years',
                'present_today',
                'inability_to_participate',
                'inability_to_participate_other',
                'study_resident',
                'relation')
        }),
        ('Status', {
            'fields': status_fields,
            'classes': ('collapse',),
        }),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj)
                + survey_schedule_fields
                + status_fields)

    radio_fields = {
        "gender": admin.VERTICAL,
        "relation": admin.VERTICAL,
        "present_today": admin.VERTICAL,
        "inability_to_participate": admin.VERTICAL,
        "study_resident": admin.VERTICAL,
        "personal_details_changed": admin.VERTICAL,
        "details_change_reason": admin.VERTICAL
    }

    list_display = (
        'first_name', 'initials',
        'household_structure',
        'relation',
        'visit_attempts',
        'inability_to_participate',
        'eligible_member',
        'eligible_subject',
        'enrollment_checklist_completed',
        'enrollment_loss_completed',
        'reported',
        'refused',
        'is_consented',
        'eligible_htc',
        'created',
        'hostname_created')

    search_fields = [
        'first_name',
        'initials',
        'household_structure__id',
        'household_structure__household__household_identifier',
        'household_structure__household__id',
        'household_structure__household__plot__plot_identifier',
        'household_structure__household__plot__id',
        'relation',
        'id']

    list_filter = (
        'household_structure__survey_schedule',
        'present_today',
        'study_resident',
        'inability_to_participate',
        'survival_status',
        'eligible_member',
        'eligible_subject',
        'enrollment_checklist_completed',
        'enrollment_loss_completed',
        'refused',
        'is_consented',
        'eligible_htc',
        'target',
        'modified',
        'hostname_created',
        'user_created',
        'visit_attempts',
        'auto_filled',
        'updated_after_auto_filled',
        'household_structure__household__plot__map_area')
