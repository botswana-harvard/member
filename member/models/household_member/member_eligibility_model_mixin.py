from django.db import models

from ...eligibile_member_helper import EligibileMemberHelper


class MemberEligibilityModelMixin(models.Model):

    eligibility_helper_cls = EligibileMemberHelper

    eligible_member = models.BooleanField(
        default=False,
        help_text='eligible to be screened. based on data on this form')

    eligible_subject = models.BooleanField(
        default=False,
        help_text=('updated by the enrollment checklist save method only. '
                   'True if subject passes the eligibility criteria.'))

    enrollment_checklist_completed = models.BooleanField(
        default=False,
        help_text=('updated by enrollment checklist only (regardless of the '
                   'eligibility outcome).'))

    enrollment_loss_completed = models.BooleanField(
        default=False,
        help_text="updated by enrollment loss save method only.")

    def save(self, *args, **kwargs):
        eligibility_helper = self.eligibility_helper_cls(**self.__dict__)
        self.eligible_member = eligibility_helper.is_eligible_member
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
