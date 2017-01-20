from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel
from edc_consent.field_mixins import SampleCollectionFieldsMixin
from edc_constants.choices import GENDER, YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE

from ..managers import MemberEntryManager

from .model_mixins import AnonymousHouseholdMemberModelMixin


class EnrollmentChecklistAnonymous(AnonymousHouseholdMemberModelMixin, SampleCollectionFieldsMixin,
                                   BaseUuidModel):
    """A model completed by the user that captures and confirms enrollment eligibility
    criteria."""

    citizen = models.CharField(
        verbose_name="Are you a Botswana citizen? ",
        max_length=3,
        choices=YES_NO,
        help_text="",
    )

    gender = models.CharField(
        choices=GENDER,
        max_length=1,
        null=True,
        blank=False)

    age_in_years = models.IntegerField(
        verbose_name='Age in years',
        validators=[MinValueValidator(16), MaxValueValidator(120)])

    guardian = models.CharField(
        verbose_name="If minor, is there a guardian available? ",
        max_length=10,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text=("If a minor age 16 and 17, ensure a guardian is available otherwise "
                   "participant will not be enrolled."))

    study_participation = models.CharField(
        verbose_name="Have you participated in a Ya Tsie Study with Botswana Harvard Partnership?",
        max_length=3,
        choices=YES_NO,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text="If 'YES' then not eligible")

    part_time_resident = models.CharField(
        verbose_name="In the past 12 months, have you typically spent 3 or "
                     "more nights per month in this community? ",
        max_length=10,
        choices=YES_NO,
        help_text="If participant has moved into the "
                  "community in the past 12 months, then "
                  "since moving in has the participant typically "
                  "spent more than 3 nights per month in this community. "
                  "If 'NO (or don't want to answer)'. Participant will not be enrolled.")

    literacy = models.CharField(
        verbose_name="Is the participant LITERATE?, or if ILLITERATE, is there a "
                     "LITERATE witness available ",
        max_length=10,
        choices=YES_NO,
        help_text="If participate is illiterate, confirm there is a literate "
                  "witness available otherwise participant will not be enrolled.")

    is_eligible = models.BooleanField(default=True)

    objects = MemberEntryManager()

    history = HistoricalRecords()

    class Meta:
        app_label = "member"
        unique_together = (('household_member', 'report_datetime'), )
        ordering = ['-report_datetime']
