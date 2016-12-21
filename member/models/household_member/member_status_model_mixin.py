from django.db import models

from edc_constants.constants import CONSENTED

from ...constants import NOT_ELIGIBLE, ELIGIBLE_FOR_SCREENING, ELIGIBLE_FOR_CONSENT


class MemberStatusModelMixin(models.Model):

    is_consented = models.BooleanField(
        default=False,
        help_text='updated by the consent model')

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def reported(self):
        return True if (self.refused or self.undecided or self.absent) else False

    @property
    def member_status(self):
        if self.is_consented:
            member_status = CONSENTED
        else:
            member_status = None
            if not self.eligible_member:
                member_status = NOT_ELIGIBLE
            if self.eligible_member:
                member_status = ELIGIBLE_FOR_SCREENING
            if self.eligible_subject:
                member_status = ELIGIBLE_FOR_CONSENT
        return member_status

    class Meta:
        abstract = True
