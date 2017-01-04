# coding=utf-8

from dateutil.relativedelta import relativedelta
from faker import Faker
from model_mommy.recipe import Recipe

from edc_base_test.utils import get_utcnow
from edc_constants.constants import NOT_APPLICABLE, YES, ALIVE, FEMALE, MALE

from .models import (
    HouseholdMember, RepresentativeEligibility, HouseholdHeadEligibility, EnrollmentChecklist,
    AbsentMember, RefusedMember, UndecidedMember, DeceasedMember, HtcMember)


fake = Faker()


householdmember = Recipe(
    HouseholdMember,
    report_datetime=get_utcnow,
    inability_to_participate=NOT_APPLICABLE,
    survival_status=ALIVE,
    age_in_years=25,
    study_resident=YES,
    gender=FEMALE,
    relation='cousin',
    subject_identifier=None,
    subject_identifier_as_pk=None,
    subject_identifier_aka=None,
    internal_identifier=None,
)

householdmember_male = Recipe(
    HouseholdMember,
    report_datetime=get_utcnow,
    inability_to_participate=NOT_APPLICABLE,
    survival_status=ALIVE,
    age_in_years=25,
    study_resident=YES,
    gender=MALE,
    relation='cousin',
    subject_identifier=None,
    subject_identifier_as_pk=None,
    subject_identifier_aka=None,
    internal_identifier=None,
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
    guardian=NOT_APPLICABLE,
    confirm_participation=NOT_APPLICABLE,
)
