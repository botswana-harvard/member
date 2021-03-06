import arrow

from django.db import models

from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_base.model_fields import OtherCharField
from edc_base.model_validators import datetime_not_future, date_not_future, eligible_if_yes
from edc_base.utils import get_utcnow
from edc_constants.choices import YES_NO

from household.choices import NEXT_APPOINTMENT_SOURCE
from survey.model_mixins import SurveyScheduleModelMixin

from ..choices import REASONS_REFUSED
from ..constants import REFUSED
from .household_member import HouseholdMember, RequiresHouseholdLogEntryMixin


class HouseholdMemberModelMixin(RequiresHouseholdLogEntryMixin,
                                SurveyScheduleModelMixin,
                                models.Model):

    """Mixin for models that need a foreignkey household_member model.
    """

    household_member = models.OneToOneField(
        HouseholdMember, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name='Report date',
        default=get_utcnow,
        validators=[datetime_not_future])

    def __str__(self):
        return str(self.household_member)

    def save(self, *args, **kwargs):
        self.survey_schedule = (
            self.household_member.survey_schedule_object.field_value)
        super().save(*args, **kwargs)

    def natural_key(self):
        return self.household_member.natural_key()
    natural_key.dependencies = ['member.householdmember', ]

    class Meta:
        abstract = True
        ordering = ['-report_datetime']


class AnonymousHouseholdMemberModelMixin(RequiresHouseholdLogEntryMixin,
                                         SurveyScheduleModelMixin,
                                         models.Model):

    """Mixin for models that need a foreignkey household_member model
    """

    household_member = models.OneToOneField(
        HouseholdMember, on_delete=models.PROTECT,
        blank=True)

    report_datetime = models.DateTimeField(
        verbose_name='Report date',
        default=get_utcnow,
        validators=[datetime_not_future])

    def __str__(self):
        return str(self.household_member)

    def save(self, *args, **kwargs):
        self.survey_schedule = (
            self.household_member.survey_schedule_object.field_value)
        super().save(*args, **kwargs)

    def natural_key(self):
        return self.household_member.natural_key()
    natural_key.dependencies = ['member.householdmember', ]

    class Meta:
        abstract = True
        ordering = ['-report_datetime']


class MemberEntryMixin(SurveyScheduleModelMixin,
                       RequiresHouseholdLogEntryMixin, models.Model):
    """For absentee and undecided log models.
    """

    household_member = models.ForeignKey(
        HouseholdMember, on_delete=models.PROTECT)

    report_date = models.DateField(
        editable=False)

    report_datetime = models.DateTimeField(
        verbose_name='Report date',
        validators=[datetime_not_future],
        default=get_utcnow)

    reason_other = OtherCharField()

    next_appt_datetime = models.DateTimeField(
        verbose_name='Follow-up appointment',
        help_text='The date and time to meet with the subject')

    next_appt_datetime_source = models.CharField(
        verbose_name='Appointment date suggested by?',
        max_length=25,
        choices=NEXT_APPOINTMENT_SOURCE,
        help_text='')

    contact_details = EncryptedCharField(
        null=True,
        blank=True,
        help_text='Information that can be used to contact someone, '
                  'preferrably the subject, to confirm the appointment')

    comment = EncryptedTextField(
        verbose_name='Comments',
        max_length=250,
        blank=True,
        null=True,
        help_text=('IMPORTANT: Do not include any names or other personally '
                   'identifying information in this comment'))

    def save(self, *args, **kwargs):
        self.survey_schedule = (
            self.household_member.survey_schedule_object.field_value)
        if not self.id and self.report_date:
            raise ValueError(
                'Expected report_date to be None. Got {}. Set report datetime, '
                'not report_date.'.format(self.report_date))
        self.report_date = arrow.Arrow.fromdatetime(
            self.report_datetime, tzinfo=self.report_datetime.tzinfo).to(
                'UTC').date()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        unique_together = ('household_member', 'report_date')


class RepresentativeEligibilityMixin(models.Model):
    """Determines if the household member is eligible representative
    of the household.

    If this form saves => eligible to be a representative.
    """

    aged_over_18 = models.CharField(
        verbose_name=(
            'Did you verify that the respondent is aged 18 or older? '),
        max_length=10,
        choices=YES_NO,
        validators=[eligible_if_yes],
        help_text=('If \'NO\' respondent cannot serve as Household '
                   'Head/Representative.'),
    )

    household_residency = models.CharField(
        verbose_name=('Does the respondent typically spend more nights on '
                      'average in this household than in any other household '
                      'in the same community?'),
        max_length=3,
        choices=YES_NO,
        help_text=('If \'NO\' respondent cannot serve as Household '
                   'Head/Representative.'),
    )

    verbal_script = models.CharField(
        verbose_name=('Did you administer the verbal script and ensure '
                      'the respondent is willing to provide household '
                      'information? '),
        max_length=10,
        choices=YES_NO,
        validators=[eligible_if_yes],
        help_text=('If \'NO\' respondent cannot serve as Household '
                   'Head/Representative.'),
    )

    class Meta:
        abstract = True


class RefusedMemberMixin(models.Model):
    """A model completed by the user that captures reasons for a
    potentially eligible household member refusing participation.
    """
    refusal_date = models.DateField(
        verbose_name='Date subject refused participation',
        validators=[date_not_future],
        help_text='Date format is YYYY-MM-DD')

    reason = models.CharField(
        verbose_name=('We respect your decision to decline. It would help us'
                      ' improve the study if you could tell us the main reason'
                      ' you do not want to participate in this study?'),
        max_length=50,
        choices=REASONS_REFUSED,
        help_text='')

    reason_other = OtherCharField()

    refused_member_status = models.CharField(
        verbose_name='Refusal status',
        max_length=100,
        help_text=('Change the refusal status from \'refused\' to \'no '
                   'longer refusing\' if and when the subject changes '
                   'their mind'),
        default=REFUSED,
        editable=False)

    comment = models.CharField(
        verbose_name='Comment',
        max_length=250,
        null=True,
        blank=True,
        help_text=(
            'IMPORTANT: Do not include any names or other personally '
            'identifying information in this comment'))

    class Meta:
        abstract = True
