import arrow

from dateutil.relativedelta import relativedelta

from django.db import models, transaction

from edc_base.utils import age, get_utcnow

from ...exceptions import CloneError
from edc_registration.models import RegisteredSubject
from member.choices import DETAILS_CHANGE_REASON
from edc_constants.choices import YES_NO


class CloneModelMixin(models.Model):

    cloned = models.BooleanField(
        default=False,
        editable=False,
        help_text=(
            'This instance was initially created by copying member information '
            'from a previous survey.')
    )

    cloned_datetime = models.DateTimeField(
        editable=False,
        null=True)

    personal_details_changed = models.CharField(
        verbose_name=(
            'Have your personal details (name/surname) changed since the '
            'last time we visited you?'),
        max_length=10,
        null=True,
        blank=False,
        choices=YES_NO,
        help_text=('personal details (name/surname)'))

    details_change_reason = models.CharField(
        verbose_name=('If YES, please specify the reason'),
        max_length=30,
        null=True,
        blank=True,
        choices=DETAILS_CHANGE_REASON,
        help_text=('if personal detail changed indicate the reason.'))

    @property
    def clone_updated(self):
        if self.cloned:
            if not self.personal_details_changed:
                return False
        return True

    def clone(self, household_structure, report_datetime, **kwargs):
        """Returns a new unsaved household member instance.

            * household_structure: the 'next' household_structure to
              which the new members will be related.
        """

        def new_age(report_datetime):
            born = (self.report_datetime
                    - relativedelta(years=self.age_in_years))
            return age(born, report_datetime).years

        with transaction.atomic():
            try:
                self.__class__.objects.get(
                    internal_identifier=self.internal_identifier,
                    household_structure=household_structure)
            except self.__class__.DoesNotExist:
                pass
            else:
                raise CloneError(
                    'Cannot clone a household member into a survey '
                    'where the member already exists')

        with transaction.atomic():
            try:
                registered_subject = RegisteredSubject.objects.get(
                    registration_identifier=self.internal_identifier)
            except RegisteredSubject.DoesNotExist:
                born = (self.report_datetime
                        - relativedelta(years=self.age_in_years))
                age_in_years = age(born, report_datetime).years
            else:
                age_in_years = age(
                    registered_subject.dob, report_datetime).years

        start = household_structure.survey_schedule_object.rstart
        end = household_structure.survey_schedule_object.rend
        rdate = arrow.Arrow.fromdatetime(
            report_datetime, report_datetime.tzinfo)

        if not (start.to('utc').date()
                <= rdate.to('utc').date()
                <= end.to('utc').date()):
            raise CloneError(
                'Invalid report datetime. \'{}\' does not fall within '
                'the date range for survey schedule \'{}\'. Expected any date '
                'from \'{}\' to \'{}\'.'.format(
                    report_datetime.strftime('%Y-%m-%d %Z'),
                    household_structure.survey_schedule_object.field_value,
                    start.to('utc').strftime('%Y-%m-%d %Z'),
                    end.to('utc').strftime('%Y-%m-%d %Z')))
        return self.__class__(
            household_structure=household_structure,
            report_datetime=report_datetime,
            first_name=self.first_name,
            initials=self.initials,
            gender=self.gender,
            age_in_years=age_in_years,
            relation=self.relation,
            internal_identifier=self.internal_identifier,
            subject_identifier=self.subject_identifier,
            subject_identifier_as_pk=self.subject_identifier_as_pk,
            cloned=True,
            cloned_datetime=get_utcnow(),
            personal_details_changed=None,
            survey_schedule=household_structure.survey_schedule,
            user_created=kwargs.get('user_created', self.user_created),
        )

    class Meta:
        abstract = True
