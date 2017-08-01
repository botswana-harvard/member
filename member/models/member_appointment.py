from django.db import models

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_constants.choices import TIME_OF_DAY, TIME_OF_WEEK

from ..managers import MemberEntryManager
from .model_mixins import HouseholdMemberModelMixin

CANCELLED_APPT = 'cancelled'
COMPLETE_APPT = 'done'
INCOMPLETE_APPT = 'incomplete'
IN_PROGRESS_APPT = 'in_progress'
NEW_APPT = 'new'

APPT_STATUS = (
    (NEW_APPT, 'New'),
    (IN_PROGRESS_APPT, 'In Progress'),
    (INCOMPLETE_APPT, 'Incomplete'),
    (COMPLETE_APPT, 'Done'),
    (CANCELLED_APPT, 'Cancelled'),
)


class MemberAppointment(HouseholdMemberModelMixin, BaseUuidModel):

    """A model created by the system and updated by the user
    for appointments.
    """

    appt_date = models.DateField(
        verbose_name=("Appointment date"),
        help_text="")

    appt_status = models.CharField(
        verbose_name=("Status"),
        choices=APPT_STATUS,
        max_length=25,
        default='new')

    label = models.CharField(
        max_length=25,
        help_text="label to group, e.g. T1 prep")

    time_of_week = models.CharField(
        verbose_name='Time of week when participant will be available',
        max_length=25,
        choices=TIME_OF_WEEK,
        blank=True,
        null=True)

    time_of_day = models.CharField(
        verbose_name='Time of day when participant will be available',
        max_length=25,
        choices=TIME_OF_DAY,
        blank=True,
        null=True,
        help_text=""
    )

    is_confirmed = models.BooleanField(default=False)

    objects = MemberEntryManager()

    history = HistoricalRecords()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'member'
        unique_together = (('household_member', 'label'), )
