from edc_base.model.models import BaseUuidModel, HistoricalRecords

from .model_mixins import HouseholdMemberModelMixin
from .model_mixins import RefusedMemberMixin


class RefusedMember (HouseholdMemberModelMixin, RefusedMemberMixin, BaseUuidModel):
    """A model completed by the user that captures reasons for a
    potentially eligible household member refusing participating in BHS."""

    # objects = HouseholdMemberManager()

    history = HistoricalRecords()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = "member"