from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel

from ..managers import MemberEntryManager

from .model_mixins import HouseholdMemberModelMixin, RefusedMemberMixin


class RefusedMember (HouseholdMemberModelMixin, RefusedMemberMixin, BaseUuidModel):
    """A model completed by the user that captures reasons for a
    potentially eligible household member refusing participating
    in BHS.
    """

    objects = MemberEntryManager()

    history = HistoricalRecords()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = "member"
