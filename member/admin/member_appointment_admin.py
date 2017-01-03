from django.contrib import admin

from ..admin_site import member_admin
from ..forms import MemberAppointmentForm
from ..models import MemberAppointment

from .modeladmin_mixins import ModelAdminMixin


@admin.register(MemberAppointment, site=member_admin)
class MemberAppointmentAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = MemberAppointmentForm

    date_hierarchy = 'appt_date'

    list_display = (
        'household_member',
        # 'survey',
        'label',
        # 'composition',
        # 'call_list',
        # 'work_list',
        'appt_date',
        'appt_status',
        'user_created',
        'user_modified',
    )

    list_filter = (
        'household_member__household_structure__survey',
        'label',
        'appt_date',
        'appt_status',
        'user_created',
        'user_modified',
        'hostname_created',
        'hostname_modified',
    )

    readonly_fields = ("household_member", )

    radio_fields = {
        'appt_status': admin.VERTICAL,
        'time_of_week': admin.VERTICAL,
        'time_of_day': admin.VERTICAL,
    }

    search_fields = (
        'household_member__first_name',
        'household_member__household_structure__pk',
        'household_member__household_structure__household__household_identifier',
        'household_member__household_structure__household__plot__plot_identifier',
    )
