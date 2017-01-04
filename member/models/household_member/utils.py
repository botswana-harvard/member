import arrow
from django.db.models import Max
from edc_constants.constants import DEAD, NOT_APPLICABLE, YES
from household.models.household_log_entry import HouseholdLogEntry
from member.exceptions import EnumerationRepresentativeError


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


def has_todays_log_entry_or_raise(household_structure):
    try:
        report_datetime = HouseholdLogEntry.objects.filter(
            household_log__household_structure=household_structure).aggregate(
                Max('report_datetime')).get('report_datetime__max')
        HouseholdLogEntry.objects.get(
            household_log__household_structure=household_structure,
            report_datetime=report_datetime)
        r = arrow.Arrow.fromdatetime(report_datetime, report_datetime.tzinfo).to('utc')
        if not r.date() == arrow.utcnow().date():
            raise EnumerationRepresentativeError(
                'Enumeration blocked. Please complete today\'s \'{}\' form first.'.format(
                    HouseholdLogEntry._meta.verbose_name))
    except HouseholdLogEntry.DoesNotExist:
        raise EnumerationRepresentativeError(
            'Enumeration blocked. Please complete today\'s \'{}\' form first.'.format(
                HouseholdLogEntry._meta.verbose_name))
