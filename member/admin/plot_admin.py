from django.contrib import admin

from ..actions import process_dispatch_available_plots
from ..admin_site import bcpp_household_admin
from ..forms import PlotForm
from ..models import Plot

from .modeladmin_mixins import ModelAdminMixin


@admin.register(Plot, site=bcpp_household_admin)
class PlotAdmin(ModelAdminMixin):

    form = PlotForm
    date_hierarchy = 'modified'
    list_per_page = 30
    list_max_show_all = 1000

    fields = (
        'status',
        'gps_degrees_s',
        'gps_minutes_s',
        'gps_degrees_e',
        'gps_minutes_e',
        'cso_number',
        'household_count',
        'eligible_members',
        'time_of_week',
        'time_of_day',
        'description')

    list_display = ('plot_identifier', 'community', 'action', 'status', 'access_attempts', 'bhs', 'htc', 'replaceable',
                    'replaced_by', 'replaces', 'cso_number', 'created', 'modified')

    list_filter = ('bhs', 'htc', 'status', 'created', 'modified', 'community', 'access_attempts', 'replaceable',
                   'hostname_modified',
                   'section', 'sub_section', 'selected', 'action', 'time_of_week', 'time_of_day')

    search_fields = ('plot_identifier', 'cso_number', 'community', 'section', 'id')

    readonly_fields = ('plot_identifier',)
    radio_fields = {
        'status': admin.VERTICAL,
        'time_of_week': admin.VERTICAL,
        'time_of_day': admin.VERTICAL,
    }
    actions = [process_dispatch_available_plots]
