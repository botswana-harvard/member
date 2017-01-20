from edc_dashboard.view_mixins import FilteredListViewMixin as BaseFilteredListViewMixin

from ....models import HouseholdMember

from ...wrappers import HouseholdMemberModelWrapper


class FilteredListViewMixin(BaseFilteredListViewMixin):

    filter_model = HouseholdMember
    filtered_model_wrapper_class = HouseholdMemberModelWrapper
    filtered_queryset_ordering = '-modified'
    url_lookup_parameters = [
        ('id', 'id'),
        ('subject_identifier', 'subject_identifier'),
        ('household_identifier', 'household_structure__household__household_identifier'),
        ('plot_identifier', 'household_structure__household__plot__plot_identifier')]
