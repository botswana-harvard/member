from django.db.models import Q

from edc_dashboard.view_mixins import FilteredListViewMixin
from edc_search.view_mixins import SearchViewMixin

from ..models import HouseholdMember

from .wrappers import HouseholdMemberModelWrapper


class MemberSearchViewMixin(SearchViewMixin):

    search_model = HouseholdMember
    search_model_wrapper_class = HouseholdMemberModelWrapper
    search_queryset_ordering = '-modified'

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


class MemberFilteredListViewMixin(FilteredListViewMixin):

    filter_model = HouseholdMember
    filtered_model_wrapper_class = HouseholdMemberModelWrapper
    filtered_queryset_ordering = '-modified'
    url_lookup_parameters = [
        'id', 'subject_identifier',
        ('household_identifier', 'household_structure__household__household_identifier'),
        ('plot_identifier', 'household_structure__household__plot__plot_identifier')]
