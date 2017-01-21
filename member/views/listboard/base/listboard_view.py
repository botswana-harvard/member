from django.views.generic import TemplateView, FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardViewMixin, AppConfigViewMixin

from survey import SurveyViewMixin


class ListboardView(ListboardViewMixin, SurveyViewMixin,
                    AppConfigViewMixin, EdcBaseViewMixin, TemplateView,
                    FormView):

    app_config_name = 'member'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            k: v for k, v in self.url_names(
                'anonymous_listboard_url_name')})
        return context
