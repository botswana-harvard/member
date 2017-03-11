from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView

from survey.view_mixins import SurveyViewMixin

from ...models import HouseholdMember
from ..wrappers import HouseholdMemberModelWrapper


class BaseListboardView(SurveyViewMixin, AppConfigViewMixin,
                        EdcBaseViewMixin, ListboardView):

    app_config_name = 'member'
    navbar_item_selected = 'member'
    navbar_name = 'default'
    model = HouseholdMember
    model_wrapper_class = HouseholdMemberModelWrapper

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_exclude_options(self, request, *args, **kwargs):
        options = super().get_queryset_exclude_options(
            request, *args, **kwargs)
        plot_identifier = django_apps.get_app_config(
            'plot').anonymous_plot_identifier
        options.update(
            {'household_structure__household__plot__plot_identifier': plot_identifier})
        return options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            k: v for k, v in self.url_names(
                'anonymous_listboard_url_name')})
        return context
