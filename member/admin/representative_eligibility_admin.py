from django.contrib import admin

from ..admin_site import member_admin
from ..forms import RepresentativeEligibilityForm
from ..models import RepresentativeEligibility

from .modeladmin_mixins import ModelAdminMixin


@admin.register(RepresentativeEligibility, site=member_admin)
class RepresentativeEligibilityAdmin(ModelAdminMixin):

    form = RepresentativeEligibilityForm
    fields = (
        "household_structure",
        "report_datetime",
        "aged_over_18",
        'household_residency',
        "verbal_script",
    )
    radio_fields = {
        "aged_over_18": admin.VERTICAL,
        "household_residency": admin.VERTICAL,
        "verbal_script": admin.VERTICAL,
    }
    list_filter = ('report_datetime', 'household_structure__household__plot__community')
