from django.apps import apps as django_apps
from django.db import models
from django.utils import timezone
from django_extensions.db.fields import UUIDField

from edc_base.model.models import HistoricalRecords, BaseUuidModel
from edc_base.utils import get_safe_random_string, safe_allowed_chars
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE

from bcpp_survey.models import Survey

from ..choices import HIV_RESULT
from ..constants import HTC, HTC_ELIGIBLE, REFUSED_HTC
from ..exceptions import MemberStatusError

from .model_mixins import HouseholdMemberModelMixin, HouseholdMemberManager
from .household_member import HouseholdMember

HIV_RESULT = list(HIV_RESULT)
HIV_RESULT.append((NOT_APPLICABLE, 'Not applicable'))
HIV_RESULT = tuple(HIV_RESULT)

app_config = django_apps.get_app_config('edc_device')


class SubjectHtc(HouseholdMemberModelMixin, BaseUuidModel):
    """A model completed by the user that captures HTC information for a household member
    not participating in BHS."""
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
        choices=YES_NO_NA,
        help_text='Required if subject accepted HTC')

    referral_clinic = models.CharField(
        verbose_name="If referred, which clinic",
        max_length=25,
        blank=True,
        null=True,
        help_text='Required if subject was referred')

    comment = models.TextField(max_length=250, null=True, blank=True)

    objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.household_member.member_status not in [HTC, HTC_ELIGIBLE, REFUSED_HTC]:
            raise MemberStatusError('Expected member status to be on of {0}. '
                                    'Got {1}'.format([HTC, HTC_ELIGIBLE, REFUSED_HTC],
                                                     self.household_member.member_status))
        self.survey = self.household_member.survey
        if not self.id:
            self.tracking_identifier = self.prepare_tracking_identifier()
        self.registered_subject = self.household_member.registered_subject
        try:
            update_fields = kwargs.get('update_fields') + ['registered_subject', 'survey', 'tracking_identifier']
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(SubjectHtc, self).save(*args, **kwargs)

    def prepare_tracking_identifier(self):
        length = 5
        template = 'HTC{device_id}{random_string}'
        opts = {'device_id': app_config.device_id, 'random_string': get_safe_random_string(length=length)}
        tracking_identifier = template.format(**opts)
        # look for a duplicate
        if self.__class__.objects.filter(tracking_identifier=tracking_identifier):
            n = 1
            while self.__class__.objects.filter(tracking_identifier=tracking_identifier):
                tracking_identifier = template.format(**opts)
                n += 1
                if n == len(safe_allowed_chars) ** length:
                    raise TypeError('Unable prepare a unique htc tracking identifier, '
                                    'all are taken. Increase the length of the random string')
        return tracking_identifier

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'bcpp_household_member'
        verbose_name = "Subject Htc"
        verbose_name_plural = "Subject Htc"


class SubjectHtcHistoryManager(HouseholdMemberManager, models.Manager):

    def get_by_natural_key(self, transaction):
        self.get(transaction=transaction)


class SubjectHtcHistory(BaseUuidModel):
    """A system model that tracks the history of deleted subject HTC instances."""
    transaction = UUIDField(unique=True)

    household_member = models.ForeignKey(HouseholdMember)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=timezone.now)

    survey = models.ForeignKey(Survey, editable=False)

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

    objects = SubjectHtcHistoryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.transaction, )

    class Meta:
        app_label = 'bcpp_household_member'
        verbose_name = 'Subject Htc History'
