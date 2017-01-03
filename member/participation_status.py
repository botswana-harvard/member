from edc_constants.constants import CONSENTED, REFUSED

from .constants import AVAILABLE, DECEASED, HTC_ELIGIBLE, ABSENT, UNDECIDED
from .models import DeceasedMember, RefusedMember, HtcMember


class ParticipationStatus:
    def __init__(self, household_member):
        if household_member.is_consented:
            participation_status = CONSENTED
            reports = [(CONSENTED, None)]
        else:
            participation_status = None
            for model, label in [
                    (DeceasedMember, DECEASED), (HtcMember, HTC_ELIGIBLE), (RefusedMember, REFUSED)]:
                try:
                    model.objects.get(household_member=household_member)
                    participation_status = label
                except model.DoesNotExist:
                    pass
            if not participation_status:
                absent_members = household_member.absentmember_set.all().order_by('report_date')
                reports = [(ABSENT, absent_member.report_date, absent_member)
                           for absent_member in absent_members]
                undecided_members = household_member.undecidedmember_set.all().order_by('report_date')
                reports.extend(
                    [(UNDECIDED, undecided_member.report_date, undecided_member)
                     for undecided_member in undecided_members])
                if reports:
                    reports.sort(key=lambda x: x[1])
                    participation_status = reports[-1:][0][0]
        self.participation_status = participation_status or AVAILABLE
        if self.participation_status in [ABSENT, UNDECIDED, AVAILABLE, HTC_ELIGIBLE]:
            self.final_status_pending = True
        else:
            self.final_status_pending = False
