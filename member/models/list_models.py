from edc_base.model.models import ListModelMixin, BaseUuidModel


class TransportMode (ListModelMixin, BaseUuidModel):

    class Meta:
        app_label = "member"


class ElectricalAppliances (ListModelMixin, BaseUuidModel):

    class Meta:
        app_label = "member"
