from edc_base_test.mixins import LoadListDataMixin, DatesTestMixin

from household.tests import HouseholdTestMixin
from plot.tests import PlotTestMixin
from survey.tests import (
    SurveyTestMixin, DatesTestMixin as SurveyDatesTestMixin)

from ..list_data import list_data

from .member_test_mixin import MemberTestMixin


class MemberMixin(PlotTestMixin, HouseholdTestMixin,
                  SurveyTestMixin, SurveyDatesTestMixin,
                  DatesTestMixin,
                  LoadListDataMixin, MemberTestMixin):

    list_data = list_data
