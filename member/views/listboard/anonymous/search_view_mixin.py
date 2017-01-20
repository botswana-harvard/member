from django.db.models import Q

from ..base import SearchViewMixin as BaseSearchViewMixin


class SearchViewMixin(BaseSearchViewMixin):

    def search_options(self, search_term, **kwargs):
        q, options = super().search_options(search_term, **kwargs)
        q = q | (
            Q(subject_identifier__icontains=search_term) |
            Q(household_structure__household__household_identifier__icontains=search_term))
        return q, options
