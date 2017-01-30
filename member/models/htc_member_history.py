from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.validators.date import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.choices import YES_NO

from .household_member import HouseholdMember


class MyManager(models.Manager):

    def get_by_natural_key(self, transaction):
        self.get(transaction=transaction)


class HtcMemberHistory(BaseUuidModel):
    """A system model that tracks the history of deleted subject
    HTC instances.
    """

    transaction = models.UUIDField(unique=True)

    household_member = models.ForeignKey(
        HouseholdMember, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    tracking_identifier = models.CharField(
        verbose_name="HTC tracking identifier",
        max_length=50,
        null=True,
        blank=True,
        help_text='Transcribe this tracking identifier onto the paper HTC Intake form.')

    offered = models.CharField(
        verbose_name="Was the subject offered HTC",
        max_length=10,
        choices=YES_NO)

    accepted = models.CharField(
        verbose_name="Did the subject accept HTC",
        max_length=25,
        choices=YES_NO)

    refusal_reason = models.CharField(
        verbose_name="If the subject did not accept HTC, please explain",
        max_length=50,
        null=True,
        blank=True,
        help_text='Required if subject did not accepted HTC')

    referred = models.CharField(
        verbose_name="Was the subject referred",
        max_length=10,
        choices=YES_NO,
        help_text='Required if subject accepted HTC')

    referral_clinic = models.CharField(
        verbose_name="If referred, which clinic",
        max_length=25,
        blank=True,
        null=True,
        help_text='Required if subject was referred')

    comment = models.TextField(max_length=250, null=True, blank=True)

    objects = MyManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.transaction, )

    class Meta:
        app_label = 'member'
        verbose_name = 'Htc member history'
        verbose_name_plural = 'Htc member history'
