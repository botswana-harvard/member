from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from .model_mixins import HouseholdMemberModelMixin, RefusedMemberMixin


class RefusedMemberHistory (HouseholdMemberModelMixin, RefusedMemberMixin, BaseUuidModel):
    """A model completed by the user that captures reasons for a
    potentially eligible household member refusing participating in BHS."""

    transaction = models.UUIDField()

    # objects = HouseholdMemberManager()

    history = HistoricalRecords()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = "member"
        verbose_name = "Refused member history"
        verbose_name_plural = "Refused member history"
