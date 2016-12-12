from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel

from ..choices import UNDECIDED_REASON

from .model_mixins import HouseholdMemberModelMixin, SubjectEntryMixin, HouseholdMemberManager
from bcpp.manager_mixins import CommunitySubsetManagerMixin


class SubjectUndecided (HouseholdMemberModelMixin, BaseUuidModel):
    """A system model that links "undecided" information to a household member."""

    objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.survey = self.household_member.survey
        self.registered_subject = self.household_member.registered_subject
        try:
            update_fields = kwargs.get('update_fields') + ['registered_subject', 'survey']
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(SubjectUndecided, self).save(*args, **kwargs)

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'bcpp_household_member'
        verbose_name = "Subject Undecided"
        verbose_name_plural = "Subject Undecided"


class SubjectUndecidedEntryManager(CommunitySubsetManagerMixin, models.Manager):

    to_reference_model = ['subject_undecided', 'household_member', 'household_structure', 'household', 'plot']

    def get_by_natural_key(self, report_datetime, household_identifier, survey_name, subject_identifier_as_pk):
        return self.get(
            report_datetime=report_datetime,
            subject_undecided__household_member__household_structure__household__household_identifier=household_identifier,
            subject_undecided__household_member__registered_subject__subject_identifier_as_pk=subject_identifier_as_pk)


class SubjectUndecidedEntry(SubjectEntryMixin, BaseUuidModel):
    """A model completed by the user that captures information on the undecided status
    of a household member potentially eligible for BHS."""
    subject_undecided = models.ForeignKey(SubjectUndecided)

    subject_undecided_reason = models.CharField(
        verbose_name="Reason",
        max_length=100,
        choices=UNDECIDED_REASON)

    objects = SubjectUndecidedEntryManager()

    history = HistoricalRecords()

    @property
    def inline_parent(self):
        return self.subject_undecided

    def natural_key(self):
        return (self.report_datetime,) + self.subject_undecided.natural_key()
    natural_key.dependencies = ['bcpp_subject.subjectundecided']

    class Meta:
        app_label = 'bcpp_household_member'
        verbose_name = "Subject Undecided Entry"
        verbose_name_plural = "Subject Undecided Entries"
        unique_together = ('subject_undecided', 'report_datetime')
