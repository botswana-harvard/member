import arrow

from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings

from edc_base.utils import get_utcnow
from edc_constants.constants import DEAD, NOT_APPLICABLE, YES, NO

from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from household.models import HouseholdLogEntry
from household.exceptions import HouseholdLogRequired
from plot.utils import get_anonymous_plot


def is_eligible_member(obj):
    """Returns True if member is eligible to complete the enrollment
    checklist.

    Note: once a member is enrolled to the study their residency
    is no longer a factor to determine eligibility for subsequent
    enrollments.
    """
    if obj.survival_status == DEAD:
        return False
    is_study_resident = (
        (not obj.cloned and obj.study_resident == YES)
        or (obj.cloned and obj.study_resident in [YES, NO])
    )
    return (
        obj.age_in_years >= 16
        and obj.age_in_years <= 64
        and is_study_resident
        and obj.inability_to_participate == NOT_APPLICABLE)


def is_child(age_in_years):
    return age_in_years < 16


def is_minor(age_in_years):
    return 16 <= age_in_years < 18


def is_adult(age_in_years):
    return 18 <= age_in_years


def is_age_eligible(age_in_years):
    return 16 <= age_in_years <= 64


def todays_log_entry_or_raise(household_structure=None,
                              report_datetime=None, **options):
    """Returns the current HouseholdLogEntry or raises a
    HouseholdLogRequired exception.

    If report_datetime is provided, use that. This means a model
    can be edited if its report_datetime matches a household log entry.

    Comparison is by date not datetime
    """

    def create_log_for_anonymous(household_structure):
        household_log_entry = HouseholdLogEntry.objects.create(
            household_log=household_structure.householdlog,
            report_datetime=get_utcnow(),
            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT,
            comment='anonymous')
        return household_log_entry

    rdate = arrow.Arrow.fromdatetime(
        report_datetime, report_datetime.tzinfo)
    # any log entries?
    anonymous_plot = get_anonymous_plot()
    if household_structure.householdlog.householdlogentry_set.all().count() == 0:
        if household_structure.household.plot == anonymous_plot:
            household_log_entry = create_log_for_anonymous(household_structure)
        else:
            raise HouseholdLogRequired(
                'No {0} records exist for \'{1}\'. \'{0}\' is required.'.format(
                    HouseholdLogEntry._meta.verbose_name.title(),
                    household_structure))
    else:
        # any log entries for given report_datetime.date?
        obj = household_structure.householdlog.householdlogentry_set.all().order_by(
            'report_datetime').last()
        last_rdate = arrow.Arrow.fromdatetime(
            obj.report_datetime, obj.report_datetime.tzinfo)
        try:
            household_log_entry = household_structure.householdlog.householdlogentry_set.get(
                report_datetime__date=rdate.to('UTC').date())
        except HouseholdLogEntry.DoesNotExist:
            if household_structure.household.plot == anonymous_plot:
                household_log_entry = create_log_for_anonymous(
                    household_structure)
            else:
                try:
                    household_log_entry = household_structure.householdlog.householdlogentry_set.get(
                        report_datetime__date=get_utcnow().date())
                except HouseholdLogEntry.DoesNotExist:
                    raise HouseholdLogRequired(
                        'A \'{}\' does not exist for {}, last log '
                        'entry was on {}.'.format(
                            HouseholdLogEntry._meta.verbose_name,
                            report_datetime.strftime('%Y-%m-%d %H:%M %Z'),
                            last_rdate.to(report_datetime.tzname()).datetime.strftime(
                                '%Y-%m-%d %H:%M %Z')))
        except MultipleObjectsReturned:
            household_log_entry = household_structure.householdlog.householdlogentry_set.filter(
                report_datetime__date=rdate.to(settings.TIME_ZONE).date()).last()
    return household_log_entry
