from edc_base.model_mixins import BaseUuidModel, ListModelMixin


class TransportMode (ListModelMixin, BaseUuidModel):

    class Meta:
        app_label = "member"


class ElectricalAppliances (ListModelMixin, BaseUuidModel):

    class Meta:
        app_label = "member"
