from django.contrib import admin

from ..admin_site import bcpp_household_admin
from ..models import GpsDevice

from .modeladmin_mixins import ModelAdminMixin


@admin.register(GpsDevice, site=bcpp_household_admin)
class GpsDeviceAdmin(ModelAdminMixin):
    instructions = []
