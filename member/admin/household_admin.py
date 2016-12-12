from django.contrib import admin

from ..forms import HouseholdForm

from ..admin_site import bcpp_household_admin
from ..models import Household

from .modeladmin_mixins import ModelAdminMixin


@admin.register(Household, site=bcpp_household_admin)
class HouseholdAdmin(ModelAdminMixin):

    form = HouseholdForm
    list_per_page = 30
    list_max_show_all = 1000

    instructions = []

    list_display = ('household_identifier', 'structure', 'plot', 'community', 'created', 'modified')

    list_filter = ('created', 'modified', 'community', 'hostname_modified')

    search_fields = ('household_identifier', 'community', 'id', 'plot__id')

    readonly_fields = ('plot', 'household_identifier', )
