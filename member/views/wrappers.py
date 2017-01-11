from django.apps import apps as django_apps

from edc_dashboard.wrappers import ModelWrapper

app_config = django_apps.get_app_config('member')


class HouseholdMemberModelWrapper(ModelWrapper):

    model_name = 'member.householdmember'
    admin_site_name = app_config.admin_site_name
    url_namespace = app_config.url_namespace
    next_url_name = app_config.listboard_url_name
    extra_querystring_attrs = {'member.householdmember': ['survey']}
    next_url_attrs = {'member.householdmember': ['household_identifier', 'survey']}
    url_instance_attrs = ['household_identifier', 'survey']

    @property
    def household_identifier(self):
        return self._original_object.household_structure.household.household_identifier

    @property
    def survey(self):
        return self._original_object.household_structure.survey_object

    @property
    def plot_identifier(self):
        return self._original_object.household_structure.household.plot.plot_identifier

    @property
    def community_name(self):
        return ' '.join(self._original_object.household_structure.household.plot.map_area.split('_'))
