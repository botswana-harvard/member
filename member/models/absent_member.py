from edc_base.model.models import HistoricalRecords, BaseUuidModel

from .model_mixins import HouseholdMemberModelMixin


class AbsentMember(HouseholdMemberModelMixin, BaseUuidModel):
    """A system model that links the absentee information with the household member."""

    # objects = HouseholdMemberManager()

    history = HistoricalRecords()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'member'
