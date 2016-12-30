from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.views.generic import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_search.forms import SearchForm
from edc_search.view_mixins import SearchViewMixin

from .models import HouseholdMember

app_config = django_apps.get_app_config('member')


class SearchPlotForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse('member:list_url')


class MembersView(EdcBaseViewMixin, TemplateView, SearchViewMixin, FormView):

    form_class = SearchPlotForm
    template_name = app_config.list_template_name
    paginate_by = 10
    search_url_name = 'household:list_url'
    search_model = HouseholdMember

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def search_options(self, search_term, **kwargs):
        q = (
            Q(subject_identifier__icontains=search_term) |
            Q(first_name__exact=search_term) |
            Q(household_structure__household__household_identifier__icontains=search_term) |
            Q(household_structure__household__plot__plot_identifier__icontains=search_term) |
            Q(user_created__iexact=search_term) |
            Q(user_modified__iexact=search_term))
        options = {}
        return q, options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = self.search_model.objects.all().order_by('-created')
        context.update(
            search_url_name=self.search_url_name,
            navbar_selected='member',
            results=self.paginate(results))
        return context
