from django.contrib import admin


from ..admin_site import member_admin
from ..forms import EnrollmentLossForm
from ..models import EnrollmentLoss

from .modeladmin_mixins import ModelAdminMixin


@admin.register(EnrollmentLoss, site=member_admin)
class EnrollmentLossAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = EnrollmentLossForm

    fields = ('household_member', 'report_datetime', 'reason')

    list_display = ('report_datetime', 'user_created', 'user_modified', 'hostname_created')

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey',
        'household_member__household_structure__household__plot__map_area')

    instructions = []
