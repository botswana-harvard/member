from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel

from ..choices import REASONS_ABSENT
from ..managers import MemberEntryManager

from .model_mixins import MemberEntryMixin


class AbsentMember(MemberEntryMixin, BaseUuidModel):
    """A model completed by the user that indicates the reason a household member
    is absent for each time the RA visits."""

    reason = models.CharField(
        verbose_name="Reason?",
        max_length=100,
        choices=REASONS_ABSENT)

    objects = MemberEntryManager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {}'.format(self.report_datetime.strftime('%Y-%m-%d'), self.reason[0:20])

    def natural_key(self):
        return (self.report_datetime, ) + self.household_member.natural_key()
    natural_key.dependencies = ['member.householdmember', ]

    class Meta(MemberEntryMixin.Meta):
        app_label = 'member'
        verbose_name = "Absent member"
        verbose_name_plural = "Absent members"
