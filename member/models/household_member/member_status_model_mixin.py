from django.db import models

from member.participation_status import ParticipationStatus


class MemberStatusModelMixin(models.Model):

    refused = models.BooleanField(
        default=False,
        help_text="updated by subject refusal save method only")

    undecided = models.BooleanField(
        default=False,
        help_text="updated by subject undecided save method only")

    absent = models.BooleanField(
        default=False,
        help_text="Updated by the subject absentee log")

    non_citizen = models.BooleanField(
        default=False,
        help_text="Updated by the enrollment checklist")

    citizen = models.BooleanField(
        default=False,
        help_text="Updated by the enrollment checklist")

    spouse_of_citizen = models.BooleanField(
        default=False,
        help_text="Updated by the enrollment checklist")

    moved = models.BooleanField(
        default=False,
        help_text="Updated by the member moved")

    @property
    def reported(self):
        return True if (
            self.refused or self.undecided or self.absent) else False

    @property
    def participation_status(self):
        return ParticipationStatus(household_member=self)

    class Meta:
        abstract = True
