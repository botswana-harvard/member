from django.db import models

from .utils import is_eligible_member


class MemberEligibilityModelMixin(models.Model):

    eligible_member = models.BooleanField(
        default=False,
        help_text='eligible to be screened. based on data on this form')

    eligible_subject = models.BooleanField(
        default=False,
        help_text=('updated by the enrollment checklist save method only. True if subject '
                   'passes the eligibility criteria.'))

    enrollment_checklist_completed = models.BooleanField(
        default=False,
        help_text=('updated by enrollment checklist only (regardless of the '
                   'eligibility outcome).'))

    enrollment_loss_completed = models.BooleanField(
        default=False,
        help_text="updated by enrollment loss save method only.")

    def save(self, *args, **kwargs):
        self.eligible_member = is_eligible_member(self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
