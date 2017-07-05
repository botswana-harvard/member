from django.core.validators import (
    MinLengthValidator, MaxLengthValidator, RegexValidator)
from django.db import models

from edc_base.exceptions import AgeValueError
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import age
from edc_constants.choices import GENDER, YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE, NO, YES

from ..age_helper import AgeHelper
from ..choices import BLOCK_CONTINUE
from ..constants import BLOCK_PARTICIPATION
from ..exceptions import MemberEnrollmentError
from ..managers import MemberEntryManager
from .model_mixins import HouseholdMemberModelMixin


class EnrollmentModelMixin(models.Model):

    age_helper_cls = AgeHelper

    is_eligible = models.BooleanField(default=False)

    age_in_years = models.IntegerField(
        null=True,
        editable=False)

    loss_reason = models.TextField(
        verbose_name='Reason not eligible',
        max_length=500,
        null=True,
        editable=False,
        help_text='(stored for the loss form)')

    non_citizen = models.BooleanField(
        default=False,
        help_text='')

    def common_clean(self):
        if not self.household_member.eligible_member:
            raise MemberEnrollmentError(
                'Member is not eligible for screening.')
        # compare values to member, raise where they dont match
        if self.dob:
            try:
                age_in_years = age(self.dob, self.report_datetime).years
            except AgeValueError as e:
                raise MemberEnrollmentError({'dob': str(e)})
            if age_in_years != self.household_member.age_in_years:
                raise MemberEnrollmentError(
                    'Age does not match member\'s age. Expected {}. Got {}'.format(
                        self.household_member.age_in_years, age_in_years),
                    'dob')
        if self.part_time_resident:
            if self.household_member.study_resident != self.part_time_resident:
                raise MemberEnrollmentError(
                    'Residency does not match member\'s residency. Expected {}'.format(
                        self.household_member.get_study_resident_display()),
                    'part_time_resident')
        if self.initials:
            if self.household_member.initials != self.initials:
                raise MemberEnrollmentError(
                    'Initials do not match member\'s initials. Expected {}'.format(
                        self.household_member.initials),
                    'initials')
        if self.gender:
            if self.household_member.gender != self.gender:
                raise MemberEnrollmentError(
                    'Gender does not match member\'s gender. Expected {}'.format(
                        self.household_member.get_gender_display()),
                    'gender')
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [MemberEnrollmentError]

    def save(self, *args, **kwargs):
        if self.dob:
            self.age_in_years = age(self.dob, self.report_datetime).years
        # is eligible or collect reasons not eligible, but do not raise an
        # exception
        loss_reason = []
        if self.has_identity == NO:
            loss_reason.append('No valid identity.')
        if self.household_residency == NO and not self.household_member.cloned:
            loss_reason.append('Failed household residency requirement')
        if self.part_time_resident == NO and not self.household_member.cloned:
            loss_reason.append(
                'Does not spend 3 or more nights per month in the community.')
        if self.citizen == NO and self.legal_marriage == NO:
            loss_reason.append('Not a citizen and not married to a citizen.')
            self.non_citizen = True
        if (self.citizen == NO and self.legal_marriage == YES and
                self.marriage_certificate == NO):
            loss_reason.append(
                'Not a citizen, married to a citizen but does not '
                'have a marriage certificate.')
            self.non_citizen = True
        if self.literacy == NO:
            loss_reason.append('Illiterate with no literate witness.')
        age_helper = self.age_helper_cls(
            age_in_years=self.household_member.age_in_years)
        if age_helper.is_minor and self.guardian != YES:
            loss_reason.append('Minor without guardian available.')
        if self.confirm_participation == BLOCK_PARTICIPATION:
            loss_reason.append('Already enrolled.')
        self.is_eligible = False if loss_reason else True
        self.loss_reason = '|'.join(loss_reason) if loss_reason else None
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class EnrollmentChecklist(EnrollmentModelMixin, HouseholdMemberModelMixin,
                          BaseUuidModel):
    """A model completed by the user that captures and confirms
    enrollment eligibility criteria.
    """

    initials = models.CharField(
        verbose_name='Initials',
        max_length=3,
        null=True,
        blank=True,
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(3),
            RegexValidator(
                '^[A-Z]{1,3}$',
                'Must be Only CAPS and 2 or 3 letters. '
                'No spaces or numbers allowed.')])

    dob = models.DateField(
        verbose_name='Date of birth',
        # validators=[dob_not_future],
        null=True,
        blank=True,
        help_text='Format is YYYY-MM-DD.')

    guardian = models.CharField(
        verbose_name='If minor, is there a guardian available? ',
        max_length=10,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text=('If a minor age 16 and 17, ensure a guardian is '
                   'available otherwise participant will not be enrolled.'))

    gender = models.CharField(
        choices=GENDER,
        max_length=1,
        null=True)

    has_identity = models.CharField(
        verbose_name=(
            '[Interviewer] Has the subject presented a valid OMANG or '
            'other identity document?'),
        max_length=10,
        choices=YES_NO,
        null=True,
        blank=True,
        help_text=(
            'Allow Omang, Passport number, driver\'s license number or Omang '
            'receipt number. If \'NO\' participant will not be enrolled.'))

    citizen = models.CharField(
        verbose_name='Are you a Botswana citizen? ',
        max_length=3,
        choices=YES_NO,
        help_text='')

    study_participation = models.CharField(
        verbose_name=(
            'Have you participated in a Ya Tsie Study with '
            'Botswana Harvard Partnership?'),
        max_length=3,
        choices=YES_NO,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text='If \'YES\' then not eligible')

    confirm_participation = models.CharField(
        verbose_name=(
            'If Yes, RA should obtain documentation of participation '
            'and ask CBS to confirm (give Omang Number). Has Participation '
            'been confirmed'),
        max_length=15,
        choices=BLOCK_CONTINUE,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text='')

    legal_marriage = models.CharField(
        verbose_name=(
            'If not a citizen, are you legally married to a Botswana Citizen?'),
        max_length=3,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text='If \'NO\' participant will not be enrolled.')

    marriage_certificate = models.CharField(
        verbose_name=(
            '[Interviewer] Has the participant produced the marriage '
            'certificate, as proof?'),
        max_length=3,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text='If \'NO\' participant will not be enrolled.')

    # same as study_resident in household member
    part_time_resident = models.CharField(
        verbose_name='In the past 12 months, have you typically spent 3 or '
                     'more nights per month in this community? ',
        max_length=10,
        choices=YES_NO,
        help_text='If participant has moved into the '
                  'community in the past 12 months, then '
                  'since moving in has the participant typically '
                  'spent more than 3 nights per month in this community. '
                  'If \'NO (or don\'t want to answer)\'. '
                  'Participant will not be enrolled.')

    household_residency = models.CharField(
        verbose_name=(
            'In the past 12 months, have you typically spent more nights '
            'on average in this household than in any other household in '
            'the same community?'),
        max_length=3,
        choices=YES_NO,
        help_text='If \'NO\' participant will not be enrolled.')

    literacy = models.CharField(
        verbose_name=(
            'Is the participant LITERATE?, or if ILLITERATE, is there a '
            'LITERATE witness available?'),
        max_length=10,
        choices=YES_NO,
        help_text=(
            'If participate is illiterate, confirm there is a literate '
            'witness available otherwise participant will not be enrolled.'))

    # TODO: what is this????
    auto_filled = models.BooleanField(
        default=False,
        editable=False,
        help_text=('Was autofilled on data conversion')
    )

    objects = MemberEntryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.report_datetime, ) + self.household_member.natural_key()
    natural_key.dependencies = ['member.householdmember', ]

    class Meta:
        app_label = 'member'
        unique_together = (('household_member', 'report_datetime'), )
        ordering = ['-report_datetime']
