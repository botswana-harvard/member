from django.contrib import admin

from ..admin_site import member_admin
from ..forms import HouseholdInfoForm
from ..models import HouseholdInfo

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(HouseholdInfo, site=member_admin)
class HouseholdInfoAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    form = HouseholdInfoForm
    fields = (
        "household_member",
        "report_datetime",
        "flooring_type",
        "flooring_type_other",
        "living_rooms",
        "water_source",
        "water_source_other",
        "energy_source",
        "energy_source_other",
        "toilet_facility",
        "toilet_facility_other",
        "electrical_appliances",
        "transport_mode",
        "goats_owned",
        "sheep_owned",
        "cattle_owned",
        "smaller_meals",
    )
    radio_fields = {
        "flooring_type": admin.VERTICAL,
        "water_source": admin.VERTICAL,
        "energy_source": admin.VERTICAL,
        "toilet_facility": admin.VERTICAL,
        "smaller_meals": admin.VERTICAL,
    }
    filter_horizontal = (
        "electrical_appliances",
        "transport_mode",
    )
    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey__survey_slug',
        'household_member__household_structure__household__plot__community')
