from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel

from bcpp.manager_mixins import CommunitySubsetManagerMixin

from ..choices import ABSENTEE_REASON

from .model_mixins import HouseholdMemberModelMixin, SubjectEntryMixin, HouseholdMemberManager


class SubjectAbsentee(HouseholdMemberModelMixin, BaseUuidModel):
    """A system model that links the absentee information with the household member."""

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
        super(SubjectAbsentee, self).save(*args, **kwargs)

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'bcpp_household_member'
        verbose_name = "Subject Absentee"
        verbose_name_plural = "Subject Absentee"


class SubjectAbsenteeEntryManager(CommunitySubsetManagerMixin, models.Manager):

    to_reference_model = ['subject_absentee', 'household_member', 'household_structure', 'household', 'plot']

    def get_by_natural_key(self, report_datetime, household_identifier, survey_name, subject_identifier_as_pk):
        return self.get(
            report_datetime=report_datetime,
            subject_absentee__household_member__household_structure__household__household_identifier=household_identifier,
            subject_absentee__household_member__registered_subject__subject_identifier_as_pk=subject_identifier_as_pk)


class SubjectAbsenteeEntry(SubjectEntryMixin, BaseUuidModel):
    """A model completed by the user that indicates the reason a household member
    is absent for each time the RA visits."""

    subject_absentee = models.ForeignKey(SubjectAbsentee)

    reason = models.CharField(
        verbose_name="Reason?",
        max_length=100,
        choices=ABSENTEE_REASON)

    objects = SubjectAbsenteeEntryManager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {}'.format(self.report_datetime.strftime('%Y-%m-%d'), self.reason[0:20])

    @property
    def inline_parent(self):
        return self.subject_absentee

    @property
    def absent(self):
        return self.subject_absentee.household_member.absent

    def natural_key(self):
        return (self.report_datetime, ) + self.subject_absentee.natural_key()
    natural_key.dependencies = ['bcpp_subject.subjectabsentee', ]

    class Meta:
        app_label = 'bcpp_household_member'
        verbose_name = "Subject Absentee Entry"
        verbose_name_plural = "Subject Absentee Entries"
        unique_together = ('subject_absentee', 'report_datetime')
