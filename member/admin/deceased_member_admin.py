from django.contrib import admin

from ..admin_site import member_admin
from ..forms import DeceasedMemberForm
from ..models import DeceasedMember

from .modeladmin_mixins import HouseholdMemberAdminMixin


@admin.register(DeceasedMember, site=member_admin)
class DeceasedMemberAdmin(HouseholdMemberAdminMixin, admin.ModelAdmin):

    form = DeceasedMemberForm

    list_display = ('household_member', 'report_datetime')

    search_fields = [
        'household_member__first_name',
        'household_member__subject_identifier',
        'household_member__household_structure__household__household_identifier']

    list_filter = (
        'report_datetime',
        'household_member__household_structure__survey__survey_slug',
        'household_member__household_structure__household__plot__community')

    radio_fields = {'relationship_death_study': admin.VERTICAL}
