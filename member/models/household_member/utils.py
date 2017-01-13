import arrow

from django.core.exceptions import MultipleObjectsReturned

from edc_constants.constants import DEAD, NOT_APPLICABLE, YES

from household.models import HouseholdLogEntry
from household.exceptions import HouseholdLogRequired


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


def todays_log_entry_or_raise(household_structure=None, report_datetime=None):
    """Returns the current HouseholdLogEntry or raises a
    HouseholdLogRequired exception.

    Comparison is by date not datetime"""
    rdate = arrow.Arrow.fromdatetime(
        report_datetime, report_datetime.tzinfo)
    # any log entries?
    household_log_entry = None
    # any log entries for given report_datetime.date?
    try:
        household_structure.householdlog.householdlogentry_set.get(
            report_datetime__date=rdate.to('utc').date())
    except HouseholdLogEntry.DoesNotExist:
        raise HouseholdLogRequired(
            'A \'{}\' does not exist for today, last log '
            'entry was on {}.'.format(
                HouseholdLogEntry._meta.verbose_name,
                report_datetime.strftime('%Y-%m-%d')))
    except MultipleObjectsReturned:
        household_structure.householdlog.householdlogentry_set.filter(
            report_datetime__date=rdate.to('utc').date()).last()
    return household_log_entry
