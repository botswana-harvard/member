from edc_base.model.models import HistoricalRecords, BaseUuidModel

from ..managers import MemberEntryManager

from .model_mixins import RepresentativeEligibilityMixin, HouseholdMemberModelMixin


class HouseholdHeadEligibility(RepresentativeEligibilityMixin,
                               HouseholdMemberModelMixin,
                               BaseUuidModel):
    """A model completed by the user that determines if the household
    member is eligible to act as a head of household or
    household representative.
    """
    objects = MemberEntryManager()

    history = HistoricalRecords()

    def __str__(self):
        return str(self.household_member)

    def natural_key(self):
        return (self.report_datetime) + self.household_member.natural_key()
    natural_key.dependencies = ['member.householdmember']

    class Meta:
        app_label = 'member'
        unique_together = ('household_member', 'aged_over_18', 'verbal_script')
        verbose_name = 'Head of household eligibility'
        verbose_name_plural = 'Head of household eligibility'
