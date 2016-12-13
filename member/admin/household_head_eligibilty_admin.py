from django.contrib import admin

from ..admin_site import member_admin
from ..models import HouseholdHeadEligibility
from ..forms import HouseholdHeadEligibilityForm

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(HouseholdHeadEligibility, site=member_admin)
class HouseholdHeadEligibilityAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    instructions = ['Important: The household member must verbally consent before completing this questionnaire.']

    form = HouseholdHeadEligibilityForm
    fields = (
        "household_member",
        "report_datetime",
        "aged_over_18",
        'household_residency',
        "verbal_script")

    radio_fields = {
        "aged_over_18": admin.VERTICAL,
        "household_residency": admin.VERTICAL,
        "verbal_script": admin.VERTICAL}

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey__survey_slug',
        'household_member__household_structure__household__plot__community')
