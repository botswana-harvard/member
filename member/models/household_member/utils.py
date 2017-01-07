import arrow

from edc_constants.constants import DEAD, NOT_APPLICABLE, YES

from household.models import is_failed_enumeration_attempt, HouseholdLogEntry

from ...exceptions import HouseholdLogRequired
from django.utils.timezone import get_current_timezone_name


def is_eligible_member(obj):
    if obj.survival_status == DEAD:
        return False
    return (
        obj.age_in_years >= 16 and obj.age_in_years <= 64 and obj.study_resident == YES and
        obj.inability_to_participate == NOT_APPLICABLE)


def is_minor(age_in_years):
    return 16 <= age_in_years < 18


def is_adult(age_in_years):
    return 18 <= age_in_years


def is_age_eligible(age_in_years):
    return 16 <= age_in_years <= 64


def has_todays_log_entry_or_raise(household_structure, report_datetime):
    """Raises an exception if date part of report_datetime does not match
    a household log entry."""
    rdate = arrow.Arrow.fromdatetime(
        report_datetime, report_datetime.tzinfo).to('utc')
    household_log_entries = household_structure.householdlog.householdlogentry_set.filter(
        report_datetime__date=rdate.date()).order_by('report_datetime')
    # no entries, so raise
    if not household_log_entries:
        raise HouseholdLogRequired(
            'A \'{}\' does not exist for report date {}.'.format(
                HouseholdLogEntry._meta.verbose_name, rdate.to(
                    get_current_timezone_name()).datetime.strftime('%Y-%m-%d')))
    # some entries, raise if all are failed attempts
    household_log_entries = [obj for obj in household_log_entries if not is_failed_enumeration_attempt(obj)]
    if not household_log_entries:
        raise HouseholdLogRequired(
            '\'{}\'s exist for report date {} but all are failed enumeration attempt.'.format(
                HouseholdLogEntry._meta.verbose_name,
                rdate.to(get_current_timezone_name()).datetime.strftime('%Y-%m-%d')))
    return household_log_entries
