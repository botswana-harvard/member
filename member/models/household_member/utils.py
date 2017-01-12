from django.core.exceptions import ObjectDoesNotExist

from edc_constants.constants import DEAD, NOT_APPLICABLE, YES
from edc_base.utils import get_utcnow


def is_eligible_member(obj):
    if obj.survival_status == DEAD:
        return False
    return (
        obj.age_in_years >= 16 and obj.age_in_years <= 64 and obj.study_resident == YES and
        obj.inability_to_participate == NOT_APPLICABLE)


def is_child(age_in_years):
    return age_in_years < 16


def is_minor(age_in_years):
    return 16 <= age_in_years < 18


def is_adult(age_in_years):
    return 18 <= age_in_years


def is_age_eligible(age_in_years):
    return 16 <= age_in_years <= 64


def clone_members(household_structure, report_datetime=None, create=None, now=None):
    report_datetime = report_datetime or get_utcnow()
    household_members = []
    survey_schedule = household_structure.survey_schedule_object
    survey_schedule = survey_schedule.previous
    while survey_schedule:
        try:
            previous = household_structure.__class__.objects.get(
                survey_schedule=survey_schedule.field_value,
                household=household_structure.household)
        except ObjectDoesNotExist:
            survey_schedule = survey_schedule.previous
        except AttributeError:
            break
        else:
            for obj in previous.householdmember_set.all():
                new_obj = obj.clone(
                    household_structure=household_structure,
                    report_datetime=report_datetime)
                if create:
                    new_obj.save()
                household_members.append(new_obj)
            if len(household_members) > 0:
                break
            else:
                survey_schedule = survey_schedule.previous
    return household_members
