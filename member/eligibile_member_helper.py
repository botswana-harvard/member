from edc_constants.constants import YES, NO, ALIVE, CONSENTED, NOT_APPLICABLE
from edc_registration.models import RegisteredSubject

from .constants import ABLE_TO_PARTICIPATE


class EligibileMemberHelper:

    def __init__(self, cloned=None, study_resident=None, survival_status=None,
                 subject_identifier=None, inability_to_participate=None,
                 age_in_years=None, **kwargs):
        self.subject_identifier = subject_identifier
        self.cloned = cloned
        self.study_resident = study_resident
        self.survival_status = survival_status
        self.inability_to_participate = inability_to_participate
        self.age_in_years = age_in_years

    @property
    def is_eligible_member(self):
        """Returns True if member is eligible to complete the enrollment
        checklist.

        Note: once a member is enrolled to the study their residency
        is no longer a factor to determine eligibility for subsequent
        enrollments.
        """
        if self.survival_status != ALIVE:
            return False
        is_study_resident = (
            (not self.cloned and self.study_resident == YES)
            or (self.cloned and self.study_resident in [YES, NO, NOT_APPLICABLE])
        )

        previously_consented = False
        try:
            registered_subject = RegisteredSubject.objects.get(
                subject_identifier=self.subject_identifier)
        except RegisteredSubject.DoesNotExist:
            pass
        else:
            if registered_subject.registration_status == CONSENTED:
                previously_consented = True

        return (
            self.age_in_years >= 16
            and (self.age_in_years <= 64 or previously_consented)
            and is_study_resident
            and self.inability_to_participate in [ABLE_TO_PARTICIPATE, NOT_APPLICABLE])
