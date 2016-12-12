from edc_base.model.models import HistoricalRecords, BaseUuidModel

from .model_mixins import HouseholdMemberModelMixin


class AbsentMember(HouseholdMemberModelMixin, BaseUuidModel):
    """A system model that links the absentee information with the household member."""

    # objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.survey = self.household_member.survey
        self.registered_subject = self.household_member.registered_subject
        try:
            update_fields = kwargs.get('update_fields') + ['registered_subject', 'survey', ]
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(AbsentMember, self).save(*args, **kwargs)

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'member'
        verbose_name = "Absent Member"
