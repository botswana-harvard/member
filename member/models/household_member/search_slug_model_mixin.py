from edc_dashboard.model_mixins import SearchSlugModelMixin as BaseSearchSlugModelMixin


class SearchSlugModelMixin(BaseSearchSlugModelMixin):

    def get_slugs(self):
        slugs = super().get_slugs()
        return slugs + [
            self.subject_identifier or '',
            self.internal_identifier or '',
            self.initials or '',
        ] + self.household_structure.get_slugs()

    class Meta:
        abstract = True
