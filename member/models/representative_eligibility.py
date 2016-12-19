from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from household.models import HouseholdStructure

from .model_mixins import RepresentativeEligibilityMixin


class RepresentativeEligibility(RepresentativeEligibilityMixin, BaseUuidModel):
    """A model completed by the user that checks the eligibility of household member
    to be the household representative."""

    report_datetime = models.DateTimeField()

    household_structure = models.OneToOneField(HouseholdStructure, on_delete=models.PROTECT)

    auto_filled = models.BooleanField(
        default=False,
        editable=False,
        help_text=('This form is autofilled for non-BHS surveys using information from a'
                   'member consented in a previous survey. See HouseholdMemberHelper')
    )

    auto_fill_member_id = models.CharField(
        max_length=50,
        null=True,
        editable=False,
        help_text='pk of household member used to autofill')

    # objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return str(self.household_structure)

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.householdstructure']

    class Meta:
        app_label = 'member'
        verbose_name = 'Household representative eligibility'
        verbose_name_plural = 'Household representative eligibility'
