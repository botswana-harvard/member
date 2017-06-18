import arrow

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned

from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO, ALIVE, CONSENTED
from edc_registration.models import RegisteredSubject

from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from household.exceptions import HouseholdLogRequired
from household.models import HouseholdLogEntry
from plot.utils import get_anonymous_plot

from ...constants import ABLE_TO_PARTICIPATE


def is_eligible_member(obj):
    """Returns True if member is eligible to complete the enrollment
    checklist.

    Note: once a member is enrolled to the study their residency
    is no longer a factor to determine eligibility for subsequent
    enrollments.
    """
    if obj.survival_status != ALIVE:
        return False
    is_study_resident = (
        (not obj.cloned and obj.study_resident == YES)
        or (obj.cloned and obj.study_resident in [YES, NO])
    )

    previously_consented = False
    try:
        registered_subject = RegisteredSubject.objects.get(
            subject_identifier=obj.subject_identifier)
    except RegisteredSubject.DoesNotExist:
        pass
    else:
        if registered_subject.registration_status == CONSENTED:
            previously_consented = True

#     consent_model = django_apps.get_model('bcpp_subject', 'subjectconsent')
#     previously_consented = False
#     if consent_model.objects.filter(subject_identifier=obj.subject_identifier).exists():
#         previously_consented = True

    return (
        obj.age_in_years >= 16
        and (obj.age_in_years <= 64 or previously_consented)
        and is_study_resident
        and obj.inability_to_participate == ABLE_TO_PARTICIPATE)


def is_child(age_in_years):
    return age_in_years < 16


def is_minor(age_in_years):
    return 16 <= age_in_years < 18


def is_adult(age_in_years):
    return 18 <= age_in_years


def is_age_eligible(age_in_years):
    return 16 <= age_in_years <= 64
