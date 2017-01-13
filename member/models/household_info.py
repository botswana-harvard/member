from django.core.exceptions import ValidationError
from django.db import models

from edc_base.model.fields import OtherCharField
from edc_base.model.models import HistoricalRecords, BaseUuidModel

from ..choices import (
    FLOORING_TYPE, WATER_SOURCE, ENERGY_SOURCE, TOILET_FACILITY, SMALLER_MEALS)

from .list_models import ElectricalAppliances, TransportMode
from household.models.household_structure.household_structure import HouseholdStructure
from edc_base.utils import get_utcnow
from ..constants import HEAD_OF_HOUSEHOLD
from ..models.household_member import HouseholdMember


class MyManager(models.Manager):

    def get_by_natural_key(self, survey_schedule, household_identifier, plot_identifier):
        return self.get(
            household_structure__survey_schedule=survey_schedule,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=household_identifier
        )


class HouseholdInfo(BaseUuidModel):
    """A model completed by the user that captures household economic status
    from the Head of Household."""

    household_structure = models.OneToOneField(HouseholdStructure, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    flooring_type = models.CharField(
        verbose_name="What is the main type of flooring for this household?",
        max_length=25,
        choices=FLOORING_TYPE,
        help_text="")

    flooring_type_other = OtherCharField()

    living_rooms = models.IntegerField(
        verbose_name=(
            "How many living rooms are there in this household unit"
            " (exclude garage, bathroom, kitchen, store-room, etc if not used as living room )? "),
        null=True,
        blank=True,
        help_text=(
            "Note: Record the number of rooms where people live/meet/sleep. If participant does not"
            " want to answer, leave blank")
    )

    water_source = models.CharField(
        verbose_name="What is the main source of drinking water for this household? ",
        max_length=35,
        choices=WATER_SOURCE,
        help_text="")

    water_source_other = OtherCharField()

    energy_source = models.CharField(
        verbose_name="What is the main source of energy used for cooking? ",
        max_length=35,
        choices=ENERGY_SOURCE,
        help_text="")

    energy_source_other = OtherCharField()

    toilet_facility = models.CharField(
        verbose_name="What is the main toilet facility used in this household? ",
        max_length=35,
        choices=TOILET_FACILITY,
        help_text="")

    toilet_facility_other = OtherCharField()

    electrical_appliances = models.ManyToManyField(
        ElectricalAppliances,
        verbose_name=(
            "Does any member of this household have any of the following that are"
            " currently working? (check all that apply)."),
        blank=True,
        help_text=("Note: Please read each response to the participant and check all that apply. "
                   "If participant does not want to answer, leave blank."))

    transport_mode = models.ManyToManyField(
        TransportMode,
        verbose_name=(
            "Does any member of this household (excluding visitors) own any of the"
            " following forms of transport in working condition? (check all that apply)."),
        blank=True,
        help_text=("Note: Please read each response to the participant and check all that apply. "
                   "If participant does not want to answer, leave blank."))

    goats_owned = models.IntegerField(
        verbose_name=(
            "How many goats are owned by the members of this household?"
            " [If unsure of exact number, give your best guess] "),
        null=True,
        blank=True,
        help_text=("Note: May need to assist in adding up goats between household members"
                   " or helping estimate. If resident does not want to answer, leave blank."))

    sheep_owned = models.IntegerField(
        verbose_name=(
            "How many sheep are owned by the members of this household?"
            " [If unsure of exact number, give your best guess] "),
        null=True,
        blank=True,
        help_text=("Note: May need to assist in adding up sheep between household members"
                   " or helping estimate. If resident does not want to answer, leave blank."))

    cattle_owned = models.IntegerField(
        verbose_name=(
            "How many head of cattle (cows and bulls) are owned by the members"
            " of this household? [If unsure of exact number, give your best guess] "),
        null=True,
        blank=True,
        help_text=("Note: May need to assist in adding up cows and bulls between household members"
                   " or helping estimate. If resident does not want to answer, leave blank."))

    smaller_meals = models.CharField(
        verbose_name=(
            "In the past 4 weeks, did you or any household member have to eat a"
            " smaller meal than you felt you needed because there was not enough food? "),
        max_length=25,
        choices=SMALLER_MEALS,
        help_text="")

    objects = MyManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.verified_household_head(self.household_structure)
        super(HouseholdInfo, self).save(*args, **kwargs)

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.householdstructure']

    def verified_household_head(self, household_structure, exception_cls=None):
        error_msg = None
        exception_cls = exception_cls or ValidationError
        try:
            household_member = HouseholdMember.objects.get(
                household_structure=self.household_structure,
                relation=HEAD_OF_HOUSEHOLD)
        except HouseholdMember.DoesNotExist:
            household_member = None
        if not household_member:
            raise exception_cls('No Household Member selected.')
        if not household_member.eligible_hoh:
            raise exception_cls('Household Member is not eligible Head Of Household. '
                                'Fill head of household eligibility first.')
        return error_msg

    class Meta:
        app_label = 'member'
        verbose_name = 'Household economic status'
        verbose_name_plural = 'Household economic status'
