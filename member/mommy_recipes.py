# coding=utf-8

from model_mommy.recipe import Recipe

from edc_base.test_mixins.reference_date_mixin import ReferenceDateMixin
from edc_constants.constants import NOT_APPLICABLE, YES

from .models import HouseholdMember, RepresentativeEligibility, HouseholdHeadEligibility


class ReferenceDate(ReferenceDateMixin):
    consent_model = 'edc_example.subjectconsent'


def get_utcnow():
    return ReferenceDate().get_utcnow()

householdmember = Recipe(
    HouseholdMember,
    age_in_years=25,
    study_resident=YES,
    inability_to_participate=NOT_APPLICABLE,
)

representativeeligibility = Recipe(
    RepresentativeEligibility,
)


householdheadeligibility = Recipe(
    HouseholdHeadEligibility,
)
