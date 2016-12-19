from django.contrib import admin

from ..admin_site import member_admin
from ..forms import HtcMemberForm
from ..models import HtcMember

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(HtcMember, site=member_admin)
class HtcMemberAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):
    form = HtcMemberForm
    dashboard_type = 'subject'
    subject_identifier_attribute = 'registration_identifier'
    fields = (
        'household_member',
        'report_datetime',
        'tracking_identifier',
        'offered',
        'accepted',
        'refusal_reason',
        'referred',
        'referral_clinic',
        'comment')

    radio_fields = {
        "offered": admin.VERTICAL,
        "accepted": admin.VERTICAL,
        "referred": admin.VERTICAL,
    }

    list_display = ('household_member', 'tracking_identifier', 'report_datetime', 'offered', 'accepted', 'referred')

    search_fields = [
        'tracking_identifier',
        'household_member__first_name',
        'household_member__household_structure__household__household_identifier']

    list_filter = (
        'report_datetime',
        'offered', 'accepted', 'referred',
        'household_member__household_structure__survey__survey_slug',
        'household_member__household_structure__household__plot__map_area')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(HtcMemberAdmin, self).get_readonly_fields(request, obj)
        return tuple(readonly_fields) + ('tracking_identifier', )
