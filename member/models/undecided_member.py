from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel

from ..choices import REASONS_UNDECIDED
from ..managers import MemberEntryManager

from .model_mixins import MemberEntryMixin


class UndecidedMember(MemberEntryMixin, BaseUuidModel):
    """A model completed by the user that captures information on the undecided status
    of a household member potentially eligible for BHS."""

    reason = models.CharField(
        verbose_name="Reason",
        max_length=100,
        choices=REASONS_UNDECIDED)

    objects = MemberEntryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.report_datetime, ) + self.household_member.natural_key()
    natural_key.dependencies = ['member.householdmember']

    class Meta:
        app_label = 'member'
        verbose_name = "Undecided member"
        verbose_name_plural = "Undecided member"
