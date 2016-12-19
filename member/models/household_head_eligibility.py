from django.core.exceptions import ValidationError

from edc_base.model.models import HistoricalRecords, BaseUuidModel

# from ..managers import HouseholdMemberManager

from .model_mixins import RepresentativeEligibilityMixin, HouseholdMemberModelMixin


class HouseholdHeadEligibility(RepresentativeEligibilityMixin, HouseholdMemberModelMixin, BaseUuidModel):
    """A model completed by the user that determines if the household member is eligible to act
    as a head of household or household representative."""

    # objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def __str__(self):
        return str(self.household_member)

    def natural_key(self):
        return self.household_member.natural_key()
    natural_key.dependencies = ['member.householdmember']

    def save(self, *args, **kwargs):
        # self.matches_household_member_values(self.household_member)
        super(HouseholdHeadEligibility, self).save(*args, **kwargs)

    def matches_household_member_values(self, household_member, exception_cls=None):
        """Compares shared values on household_member form and
        returns True if all match."""
        error_msg = None
        exception_cls = exception_cls or ValidationError
        if not household_member.age_in_years >= 18:
            raise exception_cls('Household member must be over 18 years of age. '
                                'Got {0}.'.format(household_member.age_in_years))
        return error_msg

    class Meta:
        app_label = 'member'
        unique_together = ('household_member', 'aged_over_18', 'verbal_script')
        verbose_name = 'Head of household eligibility'
        verbose_name_plural = 'Head of household eligibility'
