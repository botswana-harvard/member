from django.db import models

from edc_base.utils import get_utcnow

from household.exceptions import HouseholdLogRequired

from .utils import todays_log_entry_or_raise


class RequiresHouseholdLogEntryMixin(models.Model):

    prohibit_log_entry_by_report_datetime = False

    def common_clean(self):
        try:
            household_structure = self.household_member.household_structure
        except AttributeError:
            household_structure = self.household_structure
        if self.prohibit_log_entry_by_report_datetime:
            report_datetime = get_utcnow()
        else:
            report_datetime = self.report_datetime
        todays_log_entry_or_raise(
            household_structure=household_structure,
            report_datetime=report_datetime)
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [HouseholdLogRequired]

    class Meta:
        abstract = True
