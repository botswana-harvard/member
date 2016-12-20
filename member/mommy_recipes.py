# coding=utf-8

from dateutil.relativedelta import relativedelta
from model_mommy.recipe import Recipe

from django.apps import apps as django_apps

from edc_constants.constants import NOT_APPLICABLE, YES, ALIVE, FEMALE

from .models import (
    HouseholdMember, RepresentativeEligibility, HouseholdHeadEligibility, EnrollmentChecklist,
    AbsentMember, RefusedMember, UndecidedMember, DeceasedMember, HtcMember)


def get_utcnow():
    return django_apps.get_app_config('edc_base_test').get_utcnow()


householdmember = Recipe(
    HouseholdMember,
    report_datetime=get_utcnow,
    inability_to_participate=NOT_APPLICABLE,
    survival_status=ALIVE,
    age_in_years=25,
    study_resident=YES,
    initials='EW',
    gender=FEMALE,
)

representativeeligibility = Recipe(
    RepresentativeEligibility,
    report_datetime=get_utcnow,
)


householdheadeligibility = Recipe(
    HouseholdHeadEligibility,
    report_datetime=get_utcnow,
    aged_over_18=YES,
    household_residency=YES,
    verbal_script=YES,
)

absentmember = Recipe(
    AbsentMember,
)

refusedmember = Recipe(
    RefusedMember,
)

undecidedmember = Recipe(
    UndecidedMember,
)

deceasedmember = Recipe(
    DeceasedMember,
)

htcmember = Recipe(
    HtcMember,
)

# defaults should match defaults on householdmember
enrollmentchecklist = Recipe(
    EnrollmentChecklist,
    report_datetime=get_utcnow,
    dob=(get_utcnow() - relativedelta(years=25)).date(),
    part_time_resident=YES,
    initials='EW',
    gender=FEMALE,
    household_residency=YES,
    has_identity=YES,
    citizen=YES,
    literacy=YES,
    confirm_participation=NOT_APPLICABLE,
)
