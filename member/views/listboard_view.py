from django.apps import apps as django_apps
from django.db.models import Q

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardMixin, FilteredListViewMixin
from edc_search.view_mixins import SearchViewMixin

from .wrappers import HouseholdMemberModelWrapper

from ..models import HouseholdMember

app_config = django_apps.get_app_config('member')


class ListBoardView(EdcBaseViewMixin, ListboardMixin, FilteredListViewMixin, SearchViewMixin):

    template_name = app_config.listboard_template_name
    listboard_url_name = app_config.listboard_url_name

    search_model = HouseholdMember
    search_model_wrapper_class = HouseholdMemberModelWrapper
    search_queryset_ordering = '-modified'

    filter_model = HouseholdMember
    filtered_model_wrapper_class = HouseholdMemberModelWrapper
    filtered_queryset_ordering = '-modified'
    url_lookup_parameters = [
        'id', 'subject_identifier',
        ('household_identifier', 'household_structure__household__household_identifier'),
        ('plot_identifier', 'household_structure__household__plot__plot_identifier')]

    def search_options_for_date(self, search_term, **kwargs):
        """Adds report_datetime to search by date."""
        q, options = super().search_options_for_date(search_term, **kwargs)
        q = q | Q(report_datetime__date=search_term.date())
        return q, options

    def search_options(self, search_term, **kwargs):
        q, options = super().search_options(search_term, **kwargs)
        q = q | (
            Q(subject_identifier__icontains=search_term) |
            Q(first_name__exact=search_term) |
            Q(initials__exact=search_term) |
            Q(household_structure__household__household_identifier__icontains=search_term))
        return q, options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            navbar_selected='member',
            plot_listboard_url_name=django_apps.get_app_config('plot').listboard_url_name,
            household_listboard_url_name=django_apps.get_app_config('household').listboard_url_name,
            enumeration_listboard_url_name=django_apps.get_app_config('enumeration').listboard_url_name,
        )
        return context
