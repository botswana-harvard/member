from django.db import models

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel

from .model_mixins import HouseholdMemberModelMixin


class MyManager(models.Manager):

    def get_by_natural_key(self, transaction):
        return self.get(transaction=transaction)


class UndecidedMemberHistory (HouseholdMemberModelMixin, BaseUuidModel):
    """A system model that links "undecided" information to a
    household member.
    """

    transaction = models.UUIDField()

    objects = MyManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.transaction, )

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'member'
        verbose_name = "Undecided member history"
        verbose_name_plural = "Undecided member history"
