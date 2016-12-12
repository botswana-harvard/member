from django.contrib import admin

from ..admin_site import bcpp_household_admin
from ..forms import HouseholdAssessmentForm
from ..models import HouseholdAssessment

from .modeladmin_mixins import ModelAdminMixin


@admin.register(HouseholdAssessment, site=bcpp_household_admin)
class HouseholdAssessmentAdmin(ModelAdminMixin):

    form = HouseholdAssessmentForm

    fields = (
        'household_structure',
        'potential_eligibles',
        'eligibles_last_seen_home',
    )

    radio_fields = {
        'potential_eligibles': admin.VERTICAL,
        'eligibles_last_seen_home': admin.VERTICAL,
    }

    list_filter = ('household_structure__household__community',)
