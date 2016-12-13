from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel
from edc_base.model.validators.date import datetime_not_future

from ..choices import REASONS_UNDECIDED

from .model_mixins import MemberEntryMixin
from .undecided_member import UndecidedMember


class UndecidedMemberEntry(MemberEntryMixin, BaseUuidModel):
    """A model completed by the user that captures information on the undecided status
    of a household member potentially eligible for BHS."""
    undecided_member = models.ForeignKey(UndecidedMember)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        validators=[datetime_not_future])

    reason = models.CharField(
        verbose_name="Reason",
        max_length=100,
        choices=REASONS_UNDECIDED)

    # objects = UndecidedMemberEntryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.report_datetime, ) + self.undecided_member.natural_key()
    natural_key.dependencies = ['member.undecidedmember']

    class Meta:
        app_label = 'member'
        verbose_name = "Undecided member entry"
        verbose_name_plural = "Undecided member entries"
        unique_together = ('undecided_member', 'report_datetime')
