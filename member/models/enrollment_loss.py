from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel

from ..constants import NOT_ELIGIBLE
from ..exceptions import MemberStatusError

from .model_mixins import HouseholdMemberModelMixin, HouseholdMemberManager


class EnrollmentLoss(HouseholdMemberModelMixin, BaseUuidModel):
    """A system model auto created that captures the reason for a present BHS eligible member
    who passes BHS eligibility but is not participating in the BHS."""

    reason = models.TextField(
        verbose_name='Reason not eligible',
        max_length=500,
        help_text='Do not include any personal identifiable information.')

    objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.household_member.member_status != NOT_ELIGIBLE:
            raise MemberStatusError('Expected member status to be {0}. Got {1}'.format(
                NOT_ELIGIBLE, self.household_member.member_status))
        self.survey = self.household_member.survey
        self.registered_subject = self.household_member.registered_subject
        try:
            update_fields = kwargs.get('update_fields') + ['registered_subject', 'survey', ]
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(EnrollmentLoss, self).save(*args, **kwargs)

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'bcpp_household_member'
