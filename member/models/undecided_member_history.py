from django.db import models

from edc_base.model.models import HistoricalRecords, BaseUuidModel

from .model_mixins import HouseholdMemberModelMixin


class UndecidedMemberHistory (HouseholdMemberModelMixin, BaseUuidModel):
    """A system model that links "undecided" information to a household member."""

    transaction = models.UUIDField()

    # objects = HouseholdMemberManager()

    history = HistoricalRecords()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'member'
        verbose_name = "Undecided Member"
        verbose_name_plural = "Undecided Member"
