from edc_base_test.mixins import LoadListDataMixin

from household.tests import HouseholdTestMixin
from plot.tests import PlotTestMixin
from survey.tests import SurveyTestMixin

from ..list_data import list_data

from .member_test_mixin import MemberTestMixin
from edc_base_test.mixins.dates_test_mixin import DatesTestMixin


class MemberMixin(PlotTestMixin, HouseholdTestMixin, SurveyTestMixin, DatesTestMixin,
                  LoadListDataMixin, MemberTestMixin):

    list_data = list_data
