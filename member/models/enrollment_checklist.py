from dateutil.relativedelta import relativedelta

from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel
from edc_base.model.validators import dob_not_future
from edc_consent.validators import AgeTodayValidator
from edc_constants.choices import GENDER, YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE, NO, YES

from ..choices import BLOCK_CONTINUE
from ..exceptions import MemberEnrollmentError
from ..constants import BLOCK_PARTICIPATION

from .model_mixins import HouseholdMemberModelMixin
from .household_member import is_age_eligible, is_minor


class EnrollmentModelMixin(models.Model):

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

    def common_clean(self):
        # TODO: all these checks are very protocol specific
        # Eligibility ages ranges should be in APPS
        if self.household_member.is_consented:
            raise MemberEnrollmentError('Member is already consented')
        # compare values to member, raise where they dont match
        if self.age_in_years != self.household_member.age_in_years:
            raise MemberEnrollmentError(
                'Enrollment Checklist Age does not match Household Member age. '
                'Got {0} <> {1}'.format(self.age_in_years, self.household_member.age_in_years))
        if self.household_member.study_resident != self.part_time_resident:
            raise MemberEnrollmentError(
                'Enrollment Checklist Residency does not match Household Member residency. '
                'Got {0} <> {1}'.format(self.part_time_resident, self.household_member.study_resident))
        if self.household_member.initials != self.initials:
            raise MemberEnrollmentError(
                'Enrollment Checklist Initials do not match Household Member initials. '
                'Got {0} <> {1}'.format(self.initials, self.household_member.initials))
        if self.household_member.gender != self.gender:
            raise MemberEnrollmentError(
                'Enrollment Checklist Gender does not match Household Member gender. '
                'Got {0} <> {1}'.format(self.gender, self.household_member.gender))
        # is eligible or collect reasons not eligible, but do not raise an exception
        loss_reasons = []
        if not is_age_eligible(self.age_in_years):
            loss_reasons.append('Must be aged between >=16 and <=64 years.')
        if self.has_identity == NO:
            loss_reasons.append('No valid identity.')
        if self.household_residency == NO:
            loss_reasons.append('Failed household residency requirement')
        if self.part_time_resident == YES:
            loss_reasons.append('Does not spend 3 or more nights per month in the community.')
        if self.citizen == NO and self.legal_marriage == NO:
            loss_reasons.append('Not a citizen and not married to a citizen.')
        if (self.citizen == NO and self.legal_marriage == YES and
                self.marriage_certificate == NO):
            loss_reasons.append('Not a citizen, married to a citizen but does not have a marriage certificate.')
        if self.literacy == NO:
            loss_reasons.append('Illiterate with no literate witness.')
        if is_minor(self.household_member.age_in_years) and self.guardian != YES:
            loss_reasons.append('Minor without guardian available.')
        if self.confirm_participation == BLOCK_PARTICIPATION:
            loss_reasons.append('Already enrolled.')
        self.is_eligible = True if not loss_reasons else False
        self.loss_reason = None if not loss_reasons else '|'.join(loss_reasons)
        super().common_clean()

    def save(self, *args, **kwargs):
        self.age_in_years = relativedelta(self.report_datetime.date(), self.dob).years
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class EnrollmentChecklist(EnrollmentModelMixin, HouseholdMemberModelMixin, BaseUuidModel):
    """A model completed by the user that captures and confirms survey enrollment eligibility
    criteria."""

    initials = models.CharField(
        verbose_name='Initials',
        max_length=3,
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(3),
            RegexValidator("^[A-Z]{1,3}$", "Must be Only CAPS and 2 or 3 letters. No spaces or numbers allowed.")])

    dob = models.DateField(
        verbose_name="Date of birth",
        validators=[
            dob_not_future,
            AgeTodayValidator(16, 64)],
        null=True,
        blank=False,
        help_text="Format is YYYY-MM-DD. (Data will not be saved)")

    guardian = models.CharField(
        verbose_name="If minor, is there a guardian available? ",
        max_length=10,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="If a minor age 16 and 17, ensure a guardian is available otherwise"
                  " participant will not be enrolled.")

    gender = models.CharField(
        verbose_name="Gender",
        choices=GENDER,
        max_length=1,
        null=True,
        blank=False)

    has_identity = models.CharField(
        verbose_name="[Interviewer] Has the subject presented a valid OMANG or other identity document?",
        max_length=10,
        choices=YES_NO,
        help_text='Allow Omang, Passport number, driver\'s license number or Omang '
                  'receipt number. If \'NO\' participant will not be enrolled.')

    citizen = models.CharField(
        verbose_name="Are you a Botswana citizen? ",
        max_length=3,
        choices=YES_NO,
        help_text="")

    study_participation = models.CharField(
        verbose_name="Have you participated in a Ya Tsie Study with Botswana Harvard Partnership?",
        max_length=3,
        choices=YES_NO,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text="If 'YES' then not eligible")

    confirm_participation = models.CharField(
        verbose_name="If Yes, RA should obtain documentation of participation and ask CBS to"
                     "confirm(give Omang Number). Has Participation been confirmed",
        max_length=15,
        choices=BLOCK_CONTINUE,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text="")

    legal_marriage = models.CharField(
        verbose_name="If not a citizen, are you legally married to a Botswana Citizen?",
        max_length=3,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text="If 'NO' participant will not be enrolled.")

    marriage_certificate = models.CharField(
        verbose_name=("[Interviewer] Has the participant produced the marriage certificate, as proof? "),
        max_length=3,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text="If 'NO' participant will not be enrolled.")

    # same as study_resident in household member
    part_time_resident = models.CharField(
        verbose_name="In the past 12 months, have you typically spent 3 or"
                     " more nights per month in this community? ",
        max_length=10,
        choices=YES_NO,
        help_text="If participant has moved into the "
                  "community in the past 12 months, then "
                  "since moving in has the participant typically "
                  "spent more than 3 nights per month in this community. "
                  "If 'NO (or don't want to answer)'. Participant will not be enrolled.")

    household_residency = models.CharField(
        verbose_name='In the past 12 months, have you typically spent more nights on average '
                     'in this household than in any other household in the same community?',
        max_length=3,
        choices=YES_NO,
        help_text="If 'NO' participant will not be enrolled.")

    literacy = models.CharField(
        verbose_name="Is the participant LITERATE?, or if ILLITERATE, is there a"
                     "  LITERATE witness available ",
        max_length=10,
        choices=YES_NO,
        help_text="If participate is illiterate, confirm there is a literate"
                  "witness available otherwise participant will not be enrolled.")

    # TODO: what is this????
    auto_filled = models.BooleanField(
        default=False,
        editable=False,
        help_text=('Was autofilled on data conversion')
    )

    # objects = HouseholdMemberManager()

    history = HistoricalRecords()

#     def save(self, *args, **kwargs):
#         using = kwargs.get('using')
#         if not self.pk:
#             if self.household_member.member_status != BHS_SCREEN:
#                 raise MemberStatusError(('Expected member status to be {0}. Got {1}').format(
#                     BHS_SCREEN, self.household_member.member_status))
#         else:
#             pass
#             if not kwargs.get('update_fields'):
#                 if self.household_member.member_status not in [BHS_ELIGIBLE, NOT_ELIGIBLE, BHS_SCREEN, HTC_ELIGIBLE]:
#                     raise MemberStatusError('Expected member status to be {0}. Got {1}'.format(
#                         BHS_SCREEN + ' or ' + NOT_ELIGIBLE + ' or ' + BHS_SCREEN, self.household_member.member_status))
#         if not kwargs.get('update_fields'):
#             self.matches_household_member_values(self, self.household_member)
#         self.is_eligible, self.loss_reason = self.passes_enrollment_criteria(using)
#         super(EnrollmentChecklist, self).save(*args, **kwargs)

    class Meta:
        app_label = "member"
        unique_together = (('household_member', 'report_datetime'), )
        ordering = ['-report_datetime']
