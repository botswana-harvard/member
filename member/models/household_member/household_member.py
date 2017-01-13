from dateutil.relativedelta import relativedelta

from django.core.validators import (
    MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator, RegexValidator)
from django_crypto_fields.fields import FirstnameField
from django.db import models

from edc_base.model.fields import OtherCharField
from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.validators.date import datetime_not_future
from edc_base.utils import get_utcnow, get_uuid, age
from edc_constants.choices import YES_NO, GENDER, YES_NO_DWTA, ALIVE_DEAD_UNKNOWN
from edc_constants.constants import ALIVE, DEAD, YES
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin

from household.models import HouseholdStructure, todays_log_entry_or_raise
from household.exceptions import HouseholdLogRequired
from survey.model_mixins import SurveyScheduleModelMixin

from ...choices import DETAILS_CHANGE_REASON, INABILITY_TO_PARTICIPATE_REASON
from ...exceptions import MemberValidationError
from ...managers import HouseholdMemberManager

from .member_eligibility_model_mixin import MemberEligibilityModelMixin
from .member_identifier_model_mixin import MemberIdentifierModelMixin
from .member_status_model_mixin import MemberStatusModelMixin
from .representative_model_mixin import RepresentativeModelMixin


class HouseholdMember(UpdatesOrCreatesRegistrationModelMixin, RepresentativeModelMixin,
                      MemberStatusModelMixin, MemberEligibilityModelMixin,
                      MemberIdentifierModelMixin,
                      SurveyScheduleModelMixin, BaseUuidModel):
    """A model completed by the user to represent an enumerated household member."""

    household_structure = models.ForeignKey(HouseholdStructure, on_delete=models.PROTECT)

    internal_identifier = models.CharField(
        max_length=36,
        default=get_uuid,
        editable=False,
        help_text='Identifier to track member between surveys, '
                  'is the id of the member\'s first appearance in the table.')

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow,
        validators=[datetime_not_future])

    first_name = FirstnameField(
        verbose_name='First name',
        validators=[RegexValidator(
            "^[A-Z]{1,250}$", ("Ensure first name is only CAPS and does not contain any spaces or numbers"))])

    initials = models.CharField(
        verbose_name='Initials',
        max_length=3,
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(3),
            RegexValidator(
                "^[A-Z]{1,3}$", ("Must be Only CAPS and 2 or 3 letters. No spaces or numbers allowed."))])

    gender = models.CharField(
        verbose_name='Gender',
        max_length=1,
        choices=GENDER)

    age_in_years = models.IntegerField(
        verbose_name='Age in years',
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text=(
            "If age is unknown, enter 0. If member is less than one year old, enter 1"))

    survival_status = models.CharField(
        verbose_name='Survival status',
        max_length=10,
        default=ALIVE,
        choices=ALIVE_DEAD_UNKNOWN,
        null=True,
        blank=False)

    present_today = models.CharField(
        verbose_name='Is the member present today?',
        max_length=3,
        choices=YES_NO,
        null=True,
        blank=False)

    inability_to_participate = models.CharField(
        verbose_name="Do any of the following reasons apply to the participant?",
        max_length=17,
        null=True,
        blank=False,
        choices=INABILITY_TO_PARTICIPATE_REASON,
        help_text=("Participant can only participate if ABLE is selected. "
                   "(Any other reason make the participant unable to take "
                   "part in the informed consent process)"))

    inability_to_participate_other = OtherCharField(
        null=True)

    study_resident = models.CharField(
        verbose_name="In the past 12 months, have you typically spent 3 or "
                     "more nights per month in this community? ",
        max_length=17,
        choices=YES_NO_DWTA,
        null=True,
        blank=False,
        help_text=("If participant has moved into the "
                   "community in the past 12 months, then "
                   "since moving in has the participant typically "
                   "spent 3 or more nights per month in this community."))

    personal_details_changed = models.CharField(
        verbose_name=(
            "Have your personal details (name/surname) changed since the last time we visited you?"),
        max_length=10,
        null=True,
        blank=True,
        default='-',
        choices=YES_NO,
        help_text=('personal details (name/surname)'))

    details_change_reason = models.CharField(
        verbose_name=("If YES, please specify the reason"),
        max_length=30,
        null=True,
        blank=True,
        default='-',
        choices=DETAILS_CHANGE_REASON,
        help_text=('if personal detail changed choice a reason above.'))

    visit_attempts = models.IntegerField(
        default=0,
        help_text="")

    eligible_htc = models.BooleanField(
        default=False,
        editable=False,
        help_text="")

    refused_htc = models.BooleanField(
        default=False,
        editable=False,
        help_text="updated by subject HTC save method only")

    htc = models.BooleanField(
        default=False,
        editable=False,
        help_text="updated by the subject HTC save method only")

    target = models.IntegerField(
        default=0,
        editable=False,
    )

    auto_filled = models.BooleanField(
        default=False,
        editable=False,
        help_text=('Was autofilled for follow-up surveys using information from '
                   'previous survey. See EnumerationHelper')
    )

    auto_filled_datetime = models.DateTimeField(
        editable=False,
        null=True)

    updated_after_auto_filled = models.BooleanField(
        default=True,
        editable=False,
        help_text=('if True, a user updated the values or this was not autofilled')
    )

    additional_key = models.CharField(
        max_length=36,
        verbose_name='-',
        editable=False,
        default=None,
        null=True,
        help_text=(
            'A uuid to be added to bypass the '
            'unique constraint for firstname, initials, household_structure. '
            'Should remain as the default value for normal enumeration. Is needed '
            'for Members added to the data from the clinic section where '
            'household_structure is always the same value.'),
    )

    objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {} {}{} {}'.format(
            self.first_name, self.initials, self.age_in_years,
            self.gender, self.household_structure.survey_schedule)

    def save(self, *args, **kwargs):
        if not self.id and not self.internal_identifier:
            self.internal_identifier = get_uuid()
        self.survey_schedule = self.household_structure.survey_schedule
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.internal_identifier,) + self.household_structure.natural_key()
    natural_key.dependencies = ['household.householdstructure']

    def clone(self, household_structure, report_datetime):

        def new_age(report_datetime):
            born = report_datetime - relativedelta(years=self.age_in_years)
            return age(born, report_datetime).years

        return self.__class__(
            household_structure=household_structure,
            report_datetime=report_datetime,
            first_name=self.first_name,
            initials=self.initials,
            gender=self.gender,
            age_in_years=new_age(report_datetime),
            internal_identifier=self.internal_identifier,
            subject_identifier=self.subject_identifier,
            subject_identifier_as_pk=self.subject_identifier_as_pk,
            auto_filled=True,
            auto_filled_datetime=get_utcnow(),
            updated_after_auto_filled=False
        )

    def common_clean(self):
        if not self.id:
            todays_log_entry_or_raise(
                household_structure=self.household_structure,
                report_datetime=self.report_datetime)
        if self.survival_status == DEAD and self.present_today == YES:
            raise MemberValidationError(
                'Invalid combination. Got member status == {} but present today == {}'.format(
                    self.survival_status, self.present_today))
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        common_clean_exceptions = super().common_clean_exceptions
        common_clean_exceptions.extend([MemberValidationError, HouseholdLogRequired])
        return common_clean_exceptions

#     @property
#     def evaluate_htc_eligibility(self):
#         # from ..models import EnrollmentChecklist
#         eligible_htc = False
#         if self.age_in_years > 64 and not self.is_consented:
#             eligible_htc = True
#         elif ((not self.eligible_member and self.inability_to_participate == NOT_APPLICABLE) and
#               self.age_in_years >= 16):
#             eligible_htc = True
#         elif self.eligible_member and self.refused:
#             eligible_htc = True
#         elif self.enrollment_checklist_completed and not self.eligible_subject:
#             try:
#                 erollment_checklist = EnrollmentChecklist.objects.get(household_member=self)
#             except EnrollmentChecklist.DoesNotExist:
#                 pass
#             if erollment_checklist.confirm_participation.lower() == 'block':
#                 eligible_htc = False
#             else:
#                 eligible_htc = True
#         return eligible_htc
#

    class Meta:
        app_label = 'member'
        ordering = ['-created']
        unique_together = (
            ('subject_identifier', 'internal_identifier', 'household_structure'), )
        index_together = [['id', 'subject_identifier', 'created'], ]
