from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from ..base import ListboardView as BaseListboardView

from .filtered_list_view_mixin import FilteredListViewMixin
from .search_view_mixin import SearchViewMixin


class ListboardView(FilteredListViewMixin, SearchViewMixin, BaseListboardView):

    app_config_name = 'member'
    navbar_item_selected = 'member'
    navbar_name = 'default'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
