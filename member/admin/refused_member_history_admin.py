from django.contrib import admin

from ..admin_site import member_admin
from ..models import RefusedMemberHistory

from .modeladmin_mixins import ModelAdminMixin


@admin.register(RefusedMemberHistory, site=member_admin)
class RefusedMemberHistoryAdmin(ModelAdminMixin, admin.ModelAdmin):

    fields = (
        'household_member',
        'transaction',
        'report_datetime',
        'refusal_date',
        'reason',
        'reason_other')

    radio_fields = {"reason": admin.VERTICAL}

    list_display = ('household_member', 'report_datetime', )

    search_fields = [
        'household_member__first_name',
        'household_member__household_structure__household__household_identifier']

    list_filter = ('reason', 'household_member__household_structure__household__plot__map_area')

    instructions = []

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(RefusedMemberHistoryAdmin, self).get_readonly_fields(request, obj)
        return tuple(readonly_fields) + ('transaction', )
