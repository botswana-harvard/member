from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps as django_apps
from django.core.validators import (
    MinLengthValidator, MaxLengthValidator, MinValueValidator,
    MaxValueValidator, RegexValidator)
from django_crypto_fields.fields import FirstnameField
from django.db import models

from edc_base.model_fields import OtherCharField
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.choices import (
    GENDER, ALIVE_DEAD_UNKNOWN, YES_NO_NA, YES_NO_NA_DWTA)
from edc_constants.constants import ALIVE, DEAD, YES
from edc_search.model_mixins import SearchSlugManager
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin

from household.models import HouseholdStructure
from plot.utils import get_anonymous_plot
from survey.model_mixins import SurveyScheduleModelMixin

from ...choices import INABILITY_TO_PARTICIPATE_REASON
from ...exceptions import MemberValidationError
from ...managers import HouseholdMemberManager

from .clone_model_mixin import CloneModelMixin
from .consent_model_mixin import ConsentModelMixin
from .member_eligibility_model_mixin import MemberEligibilityModelMixin
from .member_identifier_model_mixin import MemberIdentifierModelMixin
from .member_status_model_mixin import MemberStatusModelMixin
from .representative_model_mixin import RepresentativeModelMixin
from .requires_household_log_entry_mixin import RequiresHouseholdLogEntryMixin
from .search_slug_model_mixin import SearchSlugModelMixin


class Manager(HouseholdMemberManager, SearchSlugManager):
    pass


class HouseholdMember(UpdatesOrCreatesRegistrationModelMixin,
                      RepresentativeModelMixin,
                      CloneModelMixin, ConsentModelMixin, MemberStatusModelMixin,
                      MemberEligibilityModelMixin,
                      MemberIdentifierModelMixin, RequiresHouseholdLogEntryMixin,
                      SurveyScheduleModelMixin, SearchSlugModelMixin, BaseUuidModel):
    """A model completed by the user to represent an enumerated
    household member.
    """

    household_structure = models.ForeignKey(
        HouseholdStructure, on_delete=models.PROTECT)

    household_identifier = models.CharField(
        max_length=25,
        help_text='updated on save from household')

    internal_identifier = models.UUIDField(
        default=uuid4,
        editable=False,
        help_text='Identifier to track member between surveys, '
                  'is the id of the member\'s first appearance in the table.')

    report_datetime = models.DateTimeField(
        verbose_name='Report date',
        default=get_utcnow,
        validators=[datetime_not_future])

    first_name = FirstnameField(
        verbose_name='First name',
        validators=[RegexValidator(
            '^[A-Z]{1,250}$', (
                'Ensure first name is only CAPS and does not '
                'contain any spaces or numbers'))])

    initials = models.CharField(
        verbose_name='Initials',
        max_length=3,
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(3),
            RegexValidator(
                '^[A-Z]{1,3}$', (
                    'Must be Only CAPS and 2 or 3 letters. '
                    'No spaces or numbers allowed.'))])

    gender = models.CharField(
        verbose_name='Gender',
        max_length=1,
        choices=GENDER)

    age_in_years = models.IntegerField(
        verbose_name='Age in years',
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text=(
            'If age is unknown, enter 0. If member is '
            'less than one year old, enter 1'))

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
        choices=YES_NO_NA,
        null=True,
        blank=False)

    inability_to_participate = models.CharField(
        verbose_name='Do any of the following reasons apply to the participant?',
        max_length=17,
        null=True,
        blank=False,
        choices=INABILITY_TO_PARTICIPATE_REASON,
        help_text=('Participant can only participate if ABLE is selected. '
                   '(Any other reason make the participant unable to take '
                   'part in the informed consent process)'))

    inability_to_participate_other = OtherCharField(
        null=True)

    study_resident = models.CharField(
        verbose_name='In the past 12 months, have you typically spent 3 or '
                     'more nights per month in this community? ',
        max_length=17,
        choices=YES_NO_NA_DWTA,
        null=True,
        blank=False,
        help_text=('If participant has moved into the '
                   'community in the past 12 months, then '
                   'since moving in has the participant typically '
                   'spent 3 or more nights per month in this community.'))

    visit_attempts = models.IntegerField(
        default=0,
        help_text='')

    eligible_htc = models.BooleanField(
        default=False,
        editable=False,
        help_text='')

    refused_htc = models.BooleanField(
        default=False,
        editable=False,
        help_text='updated by subject HTC save method only')

    htc = models.BooleanField(
        default=False,
        editable=False,
        help_text='updated by the subject HTC save method only')

    target = models.IntegerField(
        default=0,
        editable=False,
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
            'Should remain as the default value for normal enumeration. '
            'Is needed for Members added to the data from the clinic '
            'section where household_structure is always the same value.'),
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {} {}{} {}'.format(
            self.first_name, self.initials, self.age_in_years,
            self.gender, self.household_structure.survey_schedule)

    def save(self, *args, **kwargs):
        self.household_identifier = (
            self.household_structure.household.household_identifier)
        if not self.id and not self.internal_identifier:
            self.internal_identifier = uuid4()
        self.survey_schedule = self.household_structure.survey_schedule
        super().save(*args, **kwargs)

    def natural_key(self):
        return ((self.internal_identifier,)
                + self.household_structure.natural_key())
    natural_key.dependencies = ['household.householdstructure']

    @property
    def anonymous(self):
        """Returns True if this member resides on the anonymous plot.
        """
        plot = get_anonymous_plot()
        if self.household_structure.household.plot == plot:
            return True
        return False

    @property
    def next(self):
        """Returns a household_member instance or None that is the
        cloned household_member instance in the next
        household_structure.
        """
        next_member = None
        household_structure = self.household_structure.next
        while household_structure:
            if household_structure.next:
                try:
                    next_member = household_structure.next.householdmember_set.get(
                        internal_identifier=self.internal_identifier,
                        survey_schedule=self.survey_schedule_object.next.field_value)
                    break
                except ObjectDoesNotExist:
                    next_member = None
            else:
                next_member = None
            household_structure = self.household_structure.next
        return next_member

    @property
    def previous(self):
        """Returns a household_member instance or None that is the
        cloned household_member instance in the previous
        household_structure.
        """
        previous_member = None
        household_structure = self.household_structure.previous
        while household_structure:
            if household_structure.previous:
                try:
                    previous_member = (
                        household_structure.previous.householdmember_set.get(
                            internal_identifier=self.internal_identifier))
                    break
                except ObjectDoesNotExist:
                    try:
                        previous_member = (
                            household_structure.householdmember_set.get(
                                internal_identifier=self.internal_identifier))
                        break
                    except ObjectDoesNotExist:
                        previous_member = None
            else:
                previous_member = None
            household_structure = household_structure.previous
        return previous_member

    def common_clean(self):
        if self.survival_status == DEAD and self.present_today == YES:
            raise MemberValidationError(
                'Invalid combination. Got member status == {} but '
                'present today == {}'.format(
                    self.survival_status, self.present_today))
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [MemberValidationError]

    class Meta:
        app_label = 'member'
        ordering = ['-created']
        unique_together = (
            ('internal_identifier', 'household_structure'),
            ('first_name', 'initials', 'household_structure'))
        index_together = [['id', 'subject_identifier', 'created'], ]
