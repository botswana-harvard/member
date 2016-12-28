from django.apps import apps as django_apps
from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE

from ..choices import HIV_RESULT

from .model_mixins import HouseholdMemberModelMixin
from edc_identifier.short_identifier import ShortIdentifier

HIV_RESULT = list(HIV_RESULT)
HIV_RESULT.append((NOT_APPLICABLE, 'Not applicable'))
HIV_RESULT = tuple(HIV_RESULT)


class HtcTrackingIdentifier(ShortIdentifier):

    name = 'htctrackingidentifier'
    identifier_pattern = r'^[A-Z0-9]{6}$'
    random_string_pattern = r'^[A-Z0-9]{6}$'


class MyManager(models.Manager):

    def get_by_natural_key(self, tracking_identifier):
        self.get(tracking_identifier=tracking_identifier)


class HtcMember(HouseholdMemberModelMixin, BaseUuidModel):
    """A model completed by the user that captures HTC information for a household member
    not participating in BHS."""

    tracking_identifier = models.CharField(
        verbose_name="HTC tracking identifier",
        max_length=50,
        unique=True,
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
        choices=YES_NO_NA,
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

    def save(self, *args, **kwargs):
        if not self.id:
            self.tracking_identifier = self.prepare_tracking_identifier()
        super(HtcMember, self).save(*args, **kwargs)

    def prepare_tracking_identifier(self):
        app_config = django_apps.get_app_config('edc_device')
        return HtcTrackingIdentifier(prefix='HTC' + app_config.device_id)

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'member'
