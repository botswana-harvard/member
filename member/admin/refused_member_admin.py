from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple
from survey.admin import survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import RefusedMemberForm
from ..models import RefusedMember

from .modeladmin_mixins import ModelAdminMixin


@admin.register(RefusedMember, site=member_admin)
class RefusedMemberAdmin(ModelAdminMixin, admin.ModelAdmin):
    form = RefusedMemberForm

    fieldsets = (
        (None, {
            'fields':
            ('household_member',
             'report_datetime',
             'refusal_date',
             'reason',
             'reason_other',
             'comment')}),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {"reason": admin.VERTICAL}

    list_display = ('reason', )

    search_fields = [
        'household_member__first_name',
        'household_member__household_structure__household__household_identifier']

    list_filter = (
        'report_datetime',
        'reason',
        'household_member__household_structure__survey_schedule',
        'household_member__household_structure__household__plot__map_area')
