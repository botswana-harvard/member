from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple
from survey.admin import survey_schedule_fieldset_tuple

from ..admin_site import member_admin
from ..forms import HouseholdInfoForm
from ..models import HouseholdInfo
from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdInfo, site=member_admin)
class HouseholdInfoAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = HouseholdInfoForm

    fieldsets = (
        (None, {
            'fields': (
                "household_structure",
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
                "smaller_meals")}),
        survey_schedule_fieldset_tuple,
        audit_fieldset_tuple,
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

    search_fields = [
        'household_structure__household__household_identifier',
        'household_structure__household__plot__plot_identifier']

    list_filter = (
        'report_datetime',
        'household_structure__survey_schedule',
        'household_structure__household__plot__map_area')
