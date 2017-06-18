from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple
from survey.admin import survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import EnrollmentLossForm
from ..models import EnrollmentLoss
from .modeladmin_mixins import ModelAdminMixin


@admin.register(EnrollmentLoss, site=member_admin)
class EnrollmentLossAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = EnrollmentLossForm

    fieldsets = (
        (None, {
            'fields': (
                'household_member',
                'report_datetime',
                'reason')}),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    list_display = (
        'report_datetime', 'user_created', 'user_modified', 'hostname_created')

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey_schedule',
        'household_member__household_structure__household__plot__map_area')

    instructions = []
