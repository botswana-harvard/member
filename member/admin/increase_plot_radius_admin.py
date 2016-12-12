from django.contrib import admin

from ..actions import update_increaseplotradius_action
from ..admin_site import bcpp_household_admin
from ..filters import ActionFilter
from ..forms import IncreasePlotRadiusForm
from ..models import IncreasePlotRadius

from .modeladmin_mixins import ModelAdminMixin


@admin.register(IncreasePlotRadius, site=bcpp_household_admin)
class IncreasePlotRadiusAdmin(ModelAdminMixin):

    form = IncreasePlotRadiusForm

    fields = ('radius', )
    list_display = ('plot', 'radius', 'action', 'status', 'modified', 'created')
    list_filter = (ActionFilter, )
    search_fields = ('plot__plot_identifier', 'plot__hostname_modified')
    actions = [update_increaseplotradius_action]
