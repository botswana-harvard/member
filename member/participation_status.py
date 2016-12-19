from edc_constants.constants import CONSENTED, REFUSED

from .models import DeceasedMember, RefusedMember, AbsentMember, UndecidedMember, HtcMember
from .constants import AVAILABLE, DECEASED, HTC_ELIGIBLE, ABSENT, UNDECIDED


class ParticipationStatus:
    def __init__(self, household_member):
        if household_member.is_consented:
            participation_status = CONSENTED
        else:
            participation_status = None
            for model, label in [(DeceasedMember, DECEASED), (HtcMember, HTC_ELIGIBLE), (RefusedMember, REFUSED)]:
                try:
                    model.objects.get(household_member=household_member)
                    participation_status = label
                except model.DoesNotExist:
                    pass
            if not participation_status:
                absent_members = AbsentMember.objects.filter(
                    household_member=household_member).order_by('report_date')
                reports = [(ABSENT, absent_member.report_date) for absent_member in absent_members]
                undecided_members = UndecidedMember.objects.filter(
                    household_member=household_member).order_by('report_date')
                reports.extend(
                    [(UNDECIDED, undecided_member.report_date) for undecided_member in undecided_members])
                if reports:
                    reports.sort(key=lambda x: x[1])
                    participation_status = reports[-1:][0][0]
        self.participation_status = participation_status or AVAILABLE
