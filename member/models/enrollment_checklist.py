from datetime import date
from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel
from edc_base.model.validators import dob_not_future
from edc_consent.validators import AgeTodayValidator
from edc_constants.choices import GENDER, YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE

from ..constants import BHS_SCREEN, BHS_ELIGIBLE, NOT_ELIGIBLE, HTC_ELIGIBLE
from ..exceptions import MemberStatusError

from .model_mixins import HouseholdMemberModelMixin, HouseholdMemberManager

BLOCK_CONTINUE = (
    ('Block', 'Yes( Block from further participation)'),
    ('Continue', 'No (Can continue and participate)'),
    (NOT_APPLICABLE, 'Not applicable'),
)


class EnrollmentChecklist(HouseholdMemberModelMixin, BaseUuidModel):
    """A model completed by the user that captures and confirms BHS enrollment eligibility
    criteria."""

    initials = models.CharField(
        verbose_name='Initials',
        max_length=3,
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(3),
            RegexValidator("^[A-Z]{1,3}$", "Must be Only CAPS and 2 or 3 letters. No spaces or numbers allowed.")],
        db_index=True)

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
        default=YES_NO_NA[2][0],
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

    is_eligible = models.BooleanField(default=False)

    loss_reason = models.TextField(
        verbose_name='Reason not eligible',
        max_length=500,
        null=True,
        editable=False,
        help_text='(stored for the loss form)')

    auto_filled = models.BooleanField(
        default=False,
        editable=False,
        help_text=('Was autofilled on data conversion')
    )

    objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if not self.pk:
            if self.household_member.member_status != BHS_SCREEN:
                raise MemberStatusError(('Expected member status to be {0}. Got {1}').format(
                    BHS_SCREEN, self.household_member.member_status))
        else:
            pass
            if not kwargs.get('update_fields'):
                if self.household_member.member_status not in [BHS_ELIGIBLE, NOT_ELIGIBLE, BHS_SCREEN, HTC_ELIGIBLE]:
                    raise MemberStatusError('Expected member status to be {0}. Got {1}'.format(
                        BHS_SCREEN + ' or ' + NOT_ELIGIBLE + ' or ' + BHS_SCREEN, self.household_member.member_status))
        if not kwargs.get('update_fields'):
            self.matches_household_member_values(self, self.household_member)
        self.is_eligible, self.loss_reason = self.passes_enrollment_criteria(using)
        try:
            update_fields = kwargs.get('update_fields') + ['is_eligible', 'loss_reason', ]
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(EnrollmentChecklist, self).save(*args, **kwargs)

    def matches_household_member_values(self, enrollment_checklist, household_member, exception_cls=None):
        """Compares shared values on household_member form and returns True if all match."""
        error_msg = None
        exception_cls = exception_cls or ValidationError
        age_in_years = relativedelta(date.today(), enrollment_checklist.dob).years
        if age_in_years != household_member.age_in_years:
            error_msg = ('Enrollment Checklist Age does not match Household Member age. '
                         'Got {0} <> {1}').format(age_in_years, household_member.age_in_years)
        elif household_member.study_resident.lower() != enrollment_checklist.part_time_resident.lower():
            error_msg = ('Enrollment Checklist Residency does not match Household Member residency. '
                         'Got {0} <> {1}').format(
                             enrollment_checklist.part_time_resident, household_member.study_resident)
        elif household_member.initials.lower() != enrollment_checklist.initials.lower():
            error_msg = ('Enrollment Checklist Initials do not match Household Member initials. '
                         'Got {0} <> {1}').format(enrollment_checklist.initials, household_member.initials)
        elif household_member.gender != enrollment_checklist.gender:
            error_msg = ('Enrollment Checklist Gender does not match Household Member gender. '
                         'Got {0} <> {1}').format(enrollment_checklist.gender, household_member.gender)
        elif household_member.is_minor and age_in_years >= 18:
            error_msg = 'Household Member is a minor. Got age {0}'.format(age_in_years)
        if error_msg:
            raise exception_cls(error_msg)

    def passes_enrollment_criteria(self, using):
        """Creates or updates (or deletes) the enrollment loss based on the
        reason for not passing the enrollment checklist."""
        SubjectConsent = django_apps.get_model('bcpp_subject', 'subjectconsent')
        loss_reason = []
        age_in_years = relativedelta(date.today(), self.dob).years
        if not (SubjectConsent.objects.filter(household_member=self.household_member)):
            if not (age_in_years >= 16 and age_in_years <= 64):
                loss_reason.append('Must be aged between >=16 and <=64 years.')
            if self.has_identity.lower() == 'no':
                loss_reason.append('No valid identity.')
            if self.household_residency.lower() == 'No':
                loss_reason.append('Failed household residency requirement')
            if self.part_time_resident.lower() != 'yes':
                loss_reason.append('Does not spend 3 or more nights per month in the community.')
            if self.citizen.lower() == 'no' and self.legal_marriage.lower() == 'no':
                loss_reason.append('Not a citizen and not married to a citizen.')
            if (self.citizen.lower() == 'no' and self.legal_marriage.lower() == 'yes' and
                    self.marriage_certificate.lower() == 'no'):
                loss_reason.append('Not a citizen, married to a citizen but does not have a marriage certificate.')
            if self.literacy.lower() == 'no':
                loss_reason.append('Illiterate with no literate witness.')
            if self.household_member.is_minor and self.guardian.lower() != 'yes':
                loss_reason.append('Minor without guardian available.')
            if self.confirm_participation.lower() == 'block':
                loss_reason.append('Already enrolled.')
        return (False if loss_reason else True, loss_reason)

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = "bcpp_household_member"
        verbose_name = "Enrollment Checklist"
        unique_together = (('household_member', 'report_datetime'), )
