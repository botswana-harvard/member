from datetime import date
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator, RegexValidator)
from django.db import models
from django_crypto_fields.fields import FirstnameField
from django_crypto_fields.mask_encrypted import mask_encrypted

from edc_base.model.fields import OtherCharField
from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.validators.date import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.choices import YES_NO, GENDER, YES_NO_DWTA, ALIVE_DEAD_UNKNOWN
from edc_constants.constants import NOT_APPLICABLE, ALIVE, DEAD, YES, NO
from edc_map.site_mappers import site_mappers
from edc_registration.model_mixins import SubjectIdentifierModelMixin, UpdatesOrCreatesRegistrationModelMixin

from household.models import HouseholdStructure
from plot.models import Plot

from ..choices import HOUSEHOLD_MEMBER_PARTICIPATION, RELATIONS, DETAILS_CHANGE_REASON, INABILITY_TO_PARTICIPATE_REASON
from ..constants import ABSENT, UNDECIDED, BHS_SCREEN, REFUSED, NOT_ELIGIBLE, DECEASED, HEAD_OF_HOUSEHOLD
from ..household_member_helper import HouseholdMemberHelper
from ..exceptions import EnumerationError
from member.exceptions import EnumerationRepresentativeError


def is_eligible_member(obj):
    if obj.survival_status == DEAD:
        return False
    return (
        obj.age_in_years >= 16 and obj.age_in_years <= 64 and obj.study_resident == YES and
        obj.inability_to_participate == NOT_APPLICABLE)


class RepresentativeModelMixin(models.Model):

    relation = models.CharField(
        verbose_name="Relation to head of household",
        max_length=35,
        choices=RELATIONS,
        null=True,
        help_text="Relation to head of household")

    eligible_hoh = models.BooleanField(
        default=False,
        editable=False,
        help_text="updated by the head of household.")

    def common_clean(self):
        # confirm RepresentativeEligibility exists ...
        try:
            RepresentativeEligibility = django_apps.get_model(*'member.representativeeligibility'.split('.'))
            RepresentativeEligibility.objects.get(household_structure=self.household_structure)
        except RepresentativeEligibility.DoesNotExist:
            raise EnumerationRepresentativeError(
                'Enumeration blocked. Please complete \'{}\' form first.'.format(
                    RepresentativeEligibility._meta.verbose_name))
        # then expect the first added member to be the HEAD_OF_HOUSEHOLD ...
        try:
            household_member = self.__class__.objects.get(relation=HEAD_OF_HOUSEHOLD, eligible_member=True)
            if self.relation == HEAD_OF_HOUSEHOLD and self.id != household_member.id:
                raise EnumerationRepresentativeError('Only one member may be the head of household.')
        except self.__class__.DoesNotExist:
            household_member = None
            if self.relation != HEAD_OF_HOUSEHOLD or not is_eligible_member(self):
                raise EnumerationRepresentativeError(
                    'Enumeration blocked. Please first add one eligible member who is the head of household.')
        # then expect HouseholdHeadEligibility to be added against the member who has relation=HEAD_OF_HOUSEHOLD...
        if household_member:
            try:
                HouseholdHeadEligibility = django_apps.get_model(*'member.householdheadeligibility'.split('.'))
                HouseholdHeadEligibility.objects.get(household_member=household_member)
            except HouseholdHeadEligibility.DoesNotExist:
                raise EnumerationRepresentativeError(
                    'Further enumeration blocked. Please complete \'{}\' form first.'.format(
                        HouseholdHeadEligibility._meta.verbose_name))
        # if all OK, add members as you like ...
        super().common_clean()

    class Meta:
        abstract = True


class MemberEligibilityModelMixin(models.Model):

    eligible_subject = models.BooleanField(
        default=False,
        editable=False,
        help_text=('updated by the enrollment checklist save method only. True if subject '
                   'passes the eligibility criteria.'))

    enrollment_checklist_completed = models.BooleanField(
        default=False,
        editable=False,
        help_text=('updated by enrollment checklist only (regardless of the '
                   'eligibility outcome).'))

    enrollment_loss_completed = models.BooleanField(
        default=False,
        editable=False,
        help_text="updated by enrollment loss save method only.")

    def common_clean(self):
        super().common_clean()

    def save(self, *args, **kwargs):
        self.eligible_member = is_eligible_member(self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class MemberStatusModelMixin(models.Model):

    member_status = models.CharField(
        max_length=25,
        choices=HOUSEHOLD_MEMBER_PARTICIPATION,
        null=True,
        editable=False,
        help_text='RESEARCH, ABSENT, REFUSED, UNDECIDED',
        db_index=True)

    reported = models.BooleanField(
        default=False,
        editable=False,
        help_text="update by any of subject absentee, undecided, refusal")

    refused = models.BooleanField(
        default=False,
        editable=False,
        help_text="updated by subject refusal save method only")

    undecided = models.BooleanField(
        default=False,
        editable=False,
        help_text="updated by subject undecided save method only")

    absent = models.BooleanField(
        default=False,
        editable=False,
        help_text="Updated by the subject absentee log")

    class Meta:
        abstract = True


class HouseholdMember(RepresentativeModelMixin, MemberStatusModelMixin, MemberEligibilityModelMixin,
                      SubjectIdentifierModelMixin,
                      UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):
    """A model completed by the user to represent an enumerated household member."""

    household_structure = models.ForeignKey(HouseholdStructure, on_delete=models.PROTECT)

    internal_identifier = models.CharField(
        max_length=36,
        null=True,  # will always be set in post_save()
        default=None,
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
            "^[A-Z]{1,250}$", ("Ensure first name is only CAPS and does not contain any spaces or numbers"))],
        db_index=True)

    initials = models.CharField(
        verbose_name='Initials',
        max_length=3,
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(3),
            RegexValidator(
                "^[A-Z]{1,3}$", ("Must be Only CAPS and 2 or 3 letters. No spaces or numbers allowed."))],
        db_index=True)

    gender = models.CharField(
        verbose_name='Gender',
        max_length=1,
        choices=GENDER,
        db_index=True)

    age_in_years = models.IntegerField(
        verbose_name='Age in years',
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        db_index=True,
        null=True,
        blank=False,
        help_text=(
            "If age is unknown, enter 0. If member is less than one year old, enter 1"))

    survival_status = models.CharField(
        verbose_name='Survival status',
        max_length=10,
        default=ALIVE,
        choices=ALIVE_DEAD_UNKNOWN)

    present_today = models.CharField(
        verbose_name='Is the member present today?',
        max_length=3,
        choices=YES_NO,
        db_index=True)

    inability_to_participate = models.CharField(
        verbose_name="Do any of the following reasons apply to the participant?",
        max_length=17,
        choices=INABILITY_TO_PARTICIPATE_REASON,
        help_text=("Participant can only participate if NONE is selected. "
                   "(Any of these reasons make the participant unable to take "
                   "part in the informed consent process)"))

    inability_to_participate_other = OtherCharField(
        null=True)

    study_resident = models.CharField(
        verbose_name="In the past 12 months, have you typically spent 3 or "
                     "more nights per month in this community? ",
        max_length=17,
        choices=YES_NO_DWTA,
        help_text=("If participant has moved into the "
                   "community in the past 12 months, then "
                   "since moving in has the participant typically "
                   "spent 3 or more nights per month in this community."))

    visit_attempts = models.IntegerField(
        default=0,
        editable=False,
        help_text="")

    hiv_history = models.CharField(
        max_length=25,
        null=True,
        editable=False)

    eligible_member = models.BooleanField(
        default=False,
        editable=False,
        help_text='eligible to be screened. based on data on this form')

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

    is_consented = models.BooleanField(
        default=False,
        editable=False, help_text="updated by the subject consent save method only")

    eligible_hoh = models.BooleanField(
        default=False,
        editable=False,
        help_text="updated by the head of household enrollment checklist only.")

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

    personal_details_changed = models.CharField(
        verbose_name=("Have your personal details (name/surname) changed since the last time we visited you?"),
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

    # objects = HouseholdMemberManager()

#    history = HistoricalRecords()

#     def __str__(self):
#         try:
#             is_bhs = '' if self.is_bhs else 'non-BHS'
#         except ValidationError:
#             is_bhs = '?'
#         return '{0} {1} {2}{3} {4}{5}'.format(
#             mask_encrypted(self.first_name),
#             self.initials,
#             self.age_in_years,
#             self.gender,
#             self.survey.survey_abbrev,
#             is_bhs)

    def common_clean(self):
        super().common_clean()

    def save(self, *args, **kwargs):
        if not self.id:
            self.internal_identifier = str(uuid4())
        super().save(*args, **kwargs)

#         selected_member_status = None
#         using = kwargs.get('using')
#         clear_enrollment_fields = []
#         self.check_eligible_representative_filled(self.household_structure, using=using)
#         if self.member_status == DECEASED:
#             self.set_death_flags
#         else:
#             self.clear_death_flags
#         self.eligible_member = self.is_eligible_member
#         if self.present_today == NO and not self.survival_status == DEAD:
#             self.absent = True
#         if kwargs.get('update_fields') == ['member_status']:  # when updated by participation view
#             selected_member_status = self.member_status
#             clear_enrollment_fields = self.update_member_status(selected_member_status, clear_enrollment_fields)
#         if self.intervention and self.plot_enrolled:
#             self.eligible_htc = self.evaluate_htc_eligibility
#         elif not self.intervention:
#             self.eligible_htc = self.evaluate_htc_eligibility
#         household_member_helper = HouseholdMemberHelper(self)
#         self.member_status = household_member_helper.member_status(selected_member_status)
#         if self.auto_filled:
#             self.updated_after_auto_filled = True
#         try:
#             update_fields = kwargs.get('update_fields') + [
#                 'member_status', 'undecided', 'absent', 'refused', 'eligible_member', 'eligible_htc',
#                 'enrollment_checklist_completed', 'enrollment_loss_completed', 'htc', 'survival_status',
#                 'present_today'] + clear_enrollment_fields
#             kwargs.update({'update_fields': update_fields})
#         except TypeError:
#             pass

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['household.householdstructure']

    def update_member_status(self, selected_member_status, clear_enrollment_fields):
        if self.member_status == BHS_SCREEN:
            self.undecided = False
            self.absent = False
            self.eligible_htc = False
            self.refused_htc = False
            if self.refused:
                self.clear_refusal
            if self.enrollment_checklist_completed:
                clear_enrollment_fields = self.clear_enrollment_checklist
            if self.htc:
                self.clear_htc
        if self.member_status == REFUSED:
            if self.enrollment_checklist_completed:
                clear_enrollment_fields = self.clear_enrollment_checklist
        else:
            self.undecided = True if selected_member_status == UNDECIDED else False
            self.absent = True if selected_member_status == ABSENT else False
        if self.eligible_hoh:
            self.relation = HEAD_OF_HOUSEHOLD
        return clear_enrollment_fields

    @property
    def set_death_flags(self):
        self.survival_status = DEAD
        self.present_today = NO

    @property
    def clear_death_flags(self):
        from ..models import DeceasedMember
        self.survival_status = ALIVE
        try:
            DeceasedMember.objects.get(household_member=self).delete()
        except DeceasedMember.DoesNotExist:
            pass

    @property
    def clear_refusal(self):
        from ..models import RefusedMember
        self.refused = False
        try:
            RefusedMember.objects.get(household_member=self).delete()
        except RefusedMember.DoesNotExist:
            pass

    @property
    def clear_htc(self):
        from ..models import HtcMember
        self.htc = False
        self.eligible_htc = False
        try:
            HtcMember.objects.get(household_member=self).delete()
        except HtcMember.DoesNotExist:
            pass

    @property
    def clear_enrollment_checklist(self):
        from ..models import EnrollmentChecklist
        self.enrollment_checklist_completed = False
        self.enrollment_loss_completed = False
        self.eligible_subject = False
        try:
            EnrollmentChecklist.objects.get(household_member=self).delete()
        except EnrollmentChecklist.DoesNotExist:
            pass
        return ['enrollment_checklist_completed', 'enrollment_loss_completed', 'eligible_subject']

    @property
    def evaluate_htc_eligibility(self):
        from ..models import EnrollmentChecklist
        eligible_htc = False
        if self.age_in_years > 64 and not self.is_consented:
            eligible_htc = True
        elif ((not self.eligible_member and self.inability_to_participate == NOT_APPLICABLE) and
              self.age_in_years >= 16):
            eligible_htc = True
        elif self.eligible_member and self.refused:
            eligible_htc = True
        elif self.enrollment_checklist_completed and not self.eligible_subject:
            try:
                erollment_checklist = EnrollmentChecklist.objects.get(household_member=self)
            except EnrollmentChecklist.DoesNotExist:
                pass
            if erollment_checklist.confirm_participation.lower() == 'block':
                eligible_htc = False
            else:
                eligible_htc = True
        return eligible_htc

    @property
    def intervention(self):
        return site_mappers.get_mapper(site_mappers.current_map_area).intervention

    @property
    def plot_enrolled(self):
        return self.household_structure.household.plot.bhs

    def check_eligible_representative_filled(self, household_structure, using=None, exception_cls=None):
        """Raises an exception if the RepresentativeEligibility form has not been completed.

        Without RepresentativeEligibility, a HouseholdMember cannot be added."""
        return household_structure.check_eligible_representative_filled(using, exception_cls)

    def check_head_household(self, household_structure, using=None, exception_cls=None):
        """Raises an exception if the HeadOusehold already exists in this household structure."""
        exception_cls = exception_cls or ValidationError
        using = using or 'default'
        try:
            current_hoh = HouseholdMember.objects.get(
                household_structure=household_structure,
                relation=HEAD_OF_HOUSEHOLD)
            # If i am not a new instance then make sure i am not comparing to myself.
            if self.id and current_hoh and (self.id != current_hoh.id):
                    raise exception_cls('{0} is the head of household already. Only one member '
                                        'may be the head of household.'.format(current_hoh))
            # If i am a new instance then i could not be comparing to myself as i do not exist in the DB yet
            elif not self.id and current_hoh:
                raise exception_cls('{0} is the head of household already. Only one member '
                                    'may be the head of household.'.format(current_hoh))
        except HouseholdMember.DoesNotExist:
            pass

    def match_enrollment_checklist_values(self, household_member, exception_cls=None):
        if household_member.enrollment_checklist:
            household_member.enrollment_checklist.matches_household_member_values(
                household_member.enrollment_checklist, household_member, exception_cls)

    @property
    def enrollment_checklist(self):
        """Returns the enrollment checklist instance or None."""
        EnrollmentChecklist = django_apps.get_model('member', 'EnrollmentChecklist')
        try:
            enrollment_checklist = EnrollmentChecklist.objects.get(household_member=self)
        except EnrollmentChecklist.DoesNotExist:
            enrollment_checklist = None
        return enrollment_checklist

    @property
    def htc_member(self):
        """Returns the HtcMember instance or None."""
        HtcMember = django_apps.get_model('member', 'HtcMember')
        try:
            htc_member = HtcMember.objects.get(household_member=self)
        except HtcMember.DoesNotExist:
            htc_member = None
        return htc_member

    @property
    def bypass_household_log(self):
        try:
            return settings.BYPASS_HOUSEHOLD_LOG
        except AttributeError:
            return False

    @property
    def enrollment_options(self):
        """Returns a dictionary of household member fields that are also
        on the enrollment checklist (as a convenience)."""
        return {'gender': self.gender,
                'dob': date.today() - relativedelta(years=self.age_in_years),
                'initials': self.initials,
                'part_time_resident': self.study_resident}

    @property
    def is_minor(self):
        return (self.age_in_years >= 16 and self.age_in_years <= 17)

    @property
    def is_adult(self):
        return (self.age_in_years >= 18 and self.age_in_years <= 64)

    @property
    def is_htc_only(self):
        """Returns True if subject has participated by accepting HTC only."""
        pass

    def update_plot_on_post_save(self):
        """Updates plot member count from householdmember."""
        members = HouseholdMember.objects.filter(
            household_structure__household__plot=self.household_structure.household.plot).count()
        try:
            plot = self.household_structure.household.plot
            plot.eligible_members = members
            plot.save()  # TODO: may want to use update_fields
        except Plot.DoesNotExist:
            pass

    def update_household_member_count_on_post_save(self, sender, using=None):
        """Updates the member count on the household_structure model."""
        household_members = sender.objects.using(using).filter(
            household_structure=self.household_structure)
        self.household_structure.member_count = household_members.count()
        self.household_structure.enrolled_member_count = len(
            [household_member for household_member in household_members if household_member.is_consented])
        self.household_structure.save(using=using)

    def delete_deceased_member_on_post_save(self):
        """Deletes the death form if it exists when survival status
        changes from Dead to Alive """
        if self.survival_status == ALIVE:
            DeceasedMember = django_apps.get_model('member', 'DeceasedMember')
            try:
                DeceasedMember.objects.get(subject_identifier=self.subject_identifier).delete()
            except DeceasedMember.DoesNotExist:
                pass

    @property
    def member_status_choices(self):
        try:
            return HouseholdMemberHelper(self).member_status_choices
        except TypeError:
            return None

    @property
    def is_consented_bhs(self):
        """Returns True if the subject consent is directly related to THIS
        household_member and False if related to a previous household_member."""
        if self.is_consented and not self.consented_in_previous_survey:
            return True
        return False

    @property
    def consented_in_previous_survey(self):
        """Returns True if the member was consented in a previous survey."""
        consented_in_previous_survey = False
        try:
            for consent in self.consents:
                if self.household_structure.survey.datetime_start > consent.survey.datetime_start:
                    consented_in_previous_survey = True
                    break
        except AttributeError:
            pass
        return consented_in_previous_survey

    @property
    def show_participation_form(self):
        """Returns True for the member status participation on the
        Household Dashboard to show as a form OR False where it shows as text."""
        show = False
        if self.consented_in_previous_survey:
            show = True
        elif (not self.is_consented and not self.member_status == NOT_ELIGIBLE):
            show = True
        return show

    @property
    def is_bhs(self):
        """Returns True if the member was survey as part of the BHS."""
        plot_identifier = self.household_structure.household.plot.plot_identifier
        clinic_plot_identifier = site_mappers.get_mapper(site_mappers.current_map_area).clinic_plot.plot_identifier
        is_bhs = plot_identifier != clinic_plot_identifier
        return is_bhs

#     def is_the_household_member_for_current_survey(self):
#         """ This traps that a household member is not created for an incorrect survey setting. Edit is OK."""
#         if not self.id and settings.DEVICE_ID not in settings.SERVER_DEVICE_ID_LIST:
#             if self.household_structure.survey != Survey.objects.current_survey():
#                 raise ImproperlyConfigured(
#                     'Your device is configured to create household_member for {0}'.format(
#                         Survey.objects.current_survey()))

    class Meta:
        app_label = 'member'
        ordering = ['-created']
        unique_together = (
            ("household_structure", "first_name", "initials", "additional_key"),
            ('subject_identifier', 'household_structure'), )
        index_together = [['id', 'subject_identifier', 'created'], ]
