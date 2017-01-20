from django.apps import apps as django_apps

from ..base import FilteredListViewMixin as BaseFilteredListViewMixin


class FilteredListViewMixin(BaseFilteredListViewMixin):

    @property
    def filtered_queryset(self):
        plot_identifier = django_apps.get_app_config('plot').anonymous_plot_identifier
        return self.filter_model.objects.filter(
            household_structure__household__plot__plot_identifier=plot_identifier).order_by(
                self.filtered_queryset_ordering)
