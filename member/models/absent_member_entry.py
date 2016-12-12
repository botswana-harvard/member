from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel

from ..choices import REASONS_ABSENT

from .model_mixins import MemberEntryMixin

from .absent_member import AbsentMember


class AbsentMemberEntry(MemberEntryMixin, BaseUuidModel):
    """A model completed by the user that indicates the reason a household member
    is absent for each time the RA visits."""

    absent_member = models.ForeignKey(AbsentMember)

    reason = models.CharField(
        verbose_name="Reason?",
        max_length=100,
        choices=REASONS_ABSENT)

    # objects = AbsentMemberEntryManager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {}'.format(self.report_datetime.strftime('%Y-%m-%d'), self.reason[0:20])

    @property
    def inline_parent(self):
        return self.absent_member

    @property
    def absent(self):
        return self.absent_member.household_member.absent

    def natural_key(self):
        return (self.report_datetime, ) + self.absent_member.natural_key()
    natural_key.dependencies = ['member.absentmember', ]

    class Meta:
        app_label = 'member'
        verbose_name = "Absent Member Entry"
        verbose_name_plural = "Absent Member Entries"
        unique_together = ('absent_member', 'report_datetime')
