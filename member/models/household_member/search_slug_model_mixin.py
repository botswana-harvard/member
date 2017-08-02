from edc_search.model_mixins import SearchSlugModelMixin as BaseSearchSlugModelMixin


class SearchSlugModelMixin(BaseSearchSlugModelMixin):

    def get_search_slug_fields(self):
        return [
            'household_structure.household.household_identifier',
            'household_structure.household.plot.plot_identifier',
            'household_structure.household.plot.map_area',
            'subject_identifier',
            'internal_identifier',
            'initials']

    class Meta:
        abstract = True
