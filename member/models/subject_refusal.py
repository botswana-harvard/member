from django.db import models
from django.utils import timezone

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.model.fields import OtherCharField
from edc_base.model.validators import date_not_future

from bcpp.manager_mixins import CommunitySubsetManagerMixin
from bcpp_survey.models import Survey

from ..choices import WHY_NOPARTICIPATE_CHOICE

from .model_mixins import HouseholdMemberModelMixin, HouseholdMemberManager
from .household_member import HouseholdMember


class SubjectRefusal (HouseholdMemberModelMixin, BaseUuidModel):
    """A model completed by the user that captures reasons for a
    potentially eligible household member refusing participating in BHS."""
    refusal_date = models.DateField(
        verbose_name="Date subject refused participation",
        validators=[date_not_future],
        help_text="Date format is YYYY-MM-DD")

    reason = models.CharField(
        verbose_name="We respect your decision to decline. It would help us"
                     " improve the study if you could tell us the main reason"
                     " you do not want to participate in this study?",
        max_length=50,
        choices=WHY_NOPARTICIPATE_CHOICE,
        help_text="")

    reason_other = OtherCharField()

    subject_refusal_status = models.CharField(
        verbose_name="Refusal status",
        max_length=100,
        help_text="Change the refusal status from 'refused' to 'no longer refusing' if and"
                  " when the subject changes their mind",
        default='REFUSED',
        editable=False)

    comment = models.CharField(
        verbose_name="Comment",
        max_length=250,
        null=True,
        blank=True,
        help_text='IMPORTANT: Do not include any names or other personally identifying '
                  'information in this comment')

    objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.survey = self.household_member.survey
        self.registered_subject = self.household_member.registered_subject
        try:
            update_fields = kwargs.get('update_fields') + ['registered_subject', 'survey', ]
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(SubjectRefusal, self).save(*args, **kwargs)

    def deserialize_prep(self, **kwargs):
        # SubjectRefusal being deleted by an IncommingTransaction, we ahead and delete it.
        # Its no longer needed at all because member status changed.
        if kwargs.get('action', None) and kwargs.get('action', None) == 'D':
            self.delete()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = "bcpp_household_member"
        verbose_name = "Subject Refusal"
        verbose_name_plural = "Subject Refusal"


class SubjectRefusalHistoryManager(CommunitySubsetManagerMixin, models.Manager):

    def get_by_natural_key(self, transaction):
        return self.get(transaction=transaction)


class SubjectRefusalHistory(BaseUuidModel):
    """A system model that tracks the history of deleted refusal instances."""

    transaction = models.UUIDField()

    household_member = models.ForeignKey(HouseholdMember)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=timezone.now)

    survey = models.ForeignKey(Survey, editable=False)

    refusal_date = models.DateField(
        verbose_name="Date subject refused participation",
        help_text="Date format is YYYY-MM-DD")

    reason = models.CharField(
        verbose_name=("We respect your decision to decline. It would help us"
                      " improve the study if you could tell us the main reason"
                      " you do not want to participate in this study?"),
        max_length=50,
        choices=WHY_NOPARTICIPATE_CHOICE,
        help_text="",
    )
    reason_other = OtherCharField()

    objects = SubjectRefusalHistoryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.transaction, )

    def get_report_datetime(self):
        return self.report_datetime

    def get_registration_datetime(self):
        return self.report_datetime

    class Meta:
        app_label = 'bcpp_household_member'
        verbose_name = 'Subject Refusal History'
