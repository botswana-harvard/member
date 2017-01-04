from django.contrib import admin

from ..admin_site import member_admin
from ..models import HtcMemberHistory

from .modeladmin_mixins import ModelAdminMixin


@admin.register(HtcMemberHistory, site=member_admin)
class HtcMemberHistoryAdmin(ModelAdminMixin, admin.ModelAdmin):

    radio_fields = {"offered": admin.VERTICAL,
                    "accepted": admin.VERTICAL,
                    "referred": admin.VERTICAL}

    list_display = ('household_member', 'report_datetime', 'tracking_identifier')

    search_fields = [
        'household_member__first_name',
        'household_member__household_structure__household__household_identifier',
        'tracking_identifier']

    list_filter = ('household_member__household_structure__household__plot__map_area',
                   'report_datetime', 'offered', 'accepted', 'referred', 'referral_clinic')

    instructions = []

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(HtcMemberHistoryAdmin, self).get_readonly_fields(request, obj)
        return tuple(readonly_fields) + ('tracking_identifier', 'transaction')
