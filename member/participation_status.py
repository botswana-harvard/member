from django.core.exceptions import ObjectDoesNotExist

from edc_constants.constants import CONSENTED

from .constants import (
    AVAILABLE, DECEASED, HTC_ELIGIBLE, ABSENT, UNDECIDED, ELIGIBLE,
    INELIGIBLE, REFUSED, REFUSED_HTC, MOVED)


class ParticipationStatus:

    def __init__(self, household_member):
        participation_status = None
        if household_member.is_consented:
            participation_status = CONSENTED
        elif hasattr(household_member, 'enrollmentchecklist'):
            if household_member.enrollmentchecklist.is_eligible:
                participation_status = ELIGIBLE
            else:
                participation_status = INELIGIBLE
        else:
            try:
                household_member.deceasedmember
            except ObjectDoesNotExist:
                participation_status = None
            else:
                participation_status = DECEASED
            if not participation_status:
                try:
                    household_member.htcmember
                except ObjectDoesNotExist:
                    participation_status = None
                else:
                    participation_status = HTC_ELIGIBLE
            if not participation_status:
                try:
                    household_member.movedmember
                except ObjectDoesNotExist:
                    participation_status = None
                else:
                    participation_status = MOVED
            if not participation_status:
                try:
                    household_member.refusedmember
                except ObjectDoesNotExist:
                    participation_status = None
                else:
                    participation_status = REFUSED
            if not participation_status:
                absent_members = household_member.absentmember_set.all().order_by(
                    'report_date')
                reports = [(ABSENT, absent_member.report_date, absent_member)
                           for absent_member in absent_members]
                undecided_members = household_member.undecidedmember_set.all().order_by(
                    'report_date')
                reports.extend(
                    [(UNDECIDED, undecided_member.report_date, undecided_member)
                     for undecided_member in undecided_members])
                if reports:
                    reports.sort(key=lambda x: x[1])
                    participation_status = reports[-1:][0][0]
        self.participation_status = participation_status or AVAILABLE
        if self.participation_status in [ABSENT, UNDECIDED, AVAILABLE, HTC_ELIGIBLE, None]:
            self.final = False
        elif self.participation_status in [
                CONSENTED, REFUSED, DECEASED, REFUSED_HTC, ELIGIBLE, INELIGIBLE]:
            self.final = True
        else:
            self.final = False

    def get_display(self):
        return ' '.join(self.participation_status.split('_')).lower().capitalize()
