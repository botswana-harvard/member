from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..base import ListboardView as BaseListboardView

from .filtered_list_view_mixin import FilteredListViewMixin
from .search_view_mixin import SearchViewMixin


class ListBoardView(FilteredListViewMixin, SearchViewMixin, BaseListboardView):

    navbar_name = 'anonymous'
    navbar_item_selected = 'member'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
