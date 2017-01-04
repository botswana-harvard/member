import arrow

from django.db import models
from django.utils.timezone import get_default_timezone

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.validators.date import date_not_future
from edc_base.utils import get_utcnow

from ..managers import MemberEntryManager

from .model_mixins import HouseholdMemberModelMixin, RefusedMemberMixin


class RefusedMember (HouseholdMemberModelMixin, RefusedMemberMixin, BaseUuidModel):
    """A model completed by the user that captures reasons for a
    potentially eligible household member refusing participating in BHS."""

    report_date = models.DateField(
        verbose_name="Report date",
        validators=[date_not_future],
        default=get_utcnow,
        unique=True)

    report_datetime = models.DateTimeField(
        default=get_utcnow,
        editable=False)

    objects = MemberEntryManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.report_datetime = arrow.Arrow.fromdate(
            self.report_date, tzinfo=get_default_timezone()).to('UTC').datetime
        super().save(*args, **kwargs)

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = "member"
