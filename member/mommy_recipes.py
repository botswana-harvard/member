# coding=utf-8

from model_mommy.recipe import Recipe

from edc_base.test_mixins.reference_date_mixin import ReferenceDateMixin
from edc_constants.constants import NOT_APPLICABLE, YES, ALIVE

from .models import HouseholdMember, RepresentativeEligibility, HouseholdHeadEligibility, EnrollmentChecklist


class ReferenceDate(ReferenceDateMixin):
    consent_model = 'edc_example.subjectconsent'


def get_utcnow():
    return ReferenceDate().get_utcnow()

householdmember = Recipe(
    HouseholdMember,
    age_in_years=25,
    study_resident=YES,
    inability_to_participate=NOT_APPLICABLE,
    survival_status=ALIVE,
)

representativeeligibility = Recipe(
    RepresentativeEligibility,
)


householdheadeligibility = Recipe(
    HouseholdHeadEligibility,
    aged_over_18=YES,
    household_residency=YES,
    verbal_script=YES,
)


enrollmentchecklist = Recipe(
    EnrollmentChecklist,
)
