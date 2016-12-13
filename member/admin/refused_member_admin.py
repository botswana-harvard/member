from django.contrib import admin

from ..admin_site import member_admin
from ..forms import RefusedMemberForm
from ..models import RefusedMember

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(RefusedMember, site=member_admin)
class RefusedMemberAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):
    form = RefusedMemberForm
    dashboard_type = 'subject'
    subject_identifier_attribute = 'registration_identifier'
    fields = (
        'household_member',
        'report_datetime',
        'refusal_date',
        'reason',
        'reason_other',
        'comment')

    radio_fields = {"reason": admin.VERTICAL}

    list_display = ('reason', )

    search_fields = [
        'household_member__first_name',
        'household_member__household_structure__household__household_identifier']

    list_filter = (
        'report_datetime',
        'reason',
        'household_member__household_structure__survey__survey_slug',
        'household_member__household_structure__household__plot__community')
