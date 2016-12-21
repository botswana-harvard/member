from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel

from ..managers import MemberEntryManager

from .model_mixins import HouseholdMemberModelMixin


class EnrollmentLoss(HouseholdMemberModelMixin, BaseUuidModel):
    """A system model auto created that captures the reason for a present BHS eligible member
    who passes BHS eligibility but is not participating in the BHS."""

    reason = models.TextField(
        verbose_name='Reason not eligible',
        max_length=500,
        help_text='Do not include any personal identifiable information.')

    objects = MemberEntryManager()

    history = HistoricalRecords()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'member'
        verbose_name = 'Enrollment loss'
        verbose_name_plural = 'Enrollment loss'
