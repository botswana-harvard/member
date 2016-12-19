from edc_constants.constants import DEAD

from .constants import (
    BHS, ELIGIBLE_FOR_CONSENT, ELIGIBLE_FOR_SCREENING, REFUSED, NOT_ELIGIBLE, HTC_ELIGIBLE, REFUSED_HTC, HTC,
    ABSENT, UNDECIDED, BHS_LOSS, ANNUAL, DECEASED)


class HouseholdMemberHelper(object):

    def __init__(self, household_member=None):
        self.household_member = household_member

    def annual_member_status(self, selected_member_status):
        return (ANNUAL if selected_member_status == ELIGIBLE_FOR_SCREENING
                else selected_member_status or self.household_member.member_status)

    def update_member_status(self, selected_member_status):
        member_status = None
        if selected_member_status == DECEASED:
            return DECEASED
        elif self.household_member.is_consented and not self.household_member.absent:
            if self.household_member.consented_in_previous_survey:
                member_status = self.annual_member_status(selected_member_status)
            else:
                member_status = BHS
        elif (not member_status) and self.household_member.eligible_subject:
            member_status = ELIGIBLE_FOR_CONSENT
        elif ((self.household_member.undecided or self.household_member.absent or
               self.household_member.refused) and selected_member_status == ELIGIBLE_FOR_SCREENING):
            member_status = ELIGIBLE_FOR_SCREENING
        elif ((self.household_member.absent or selected_member_status == ABSENT) and
              self.household_member.eligible_member):
            member_status = ABSENT
        elif ((self.household_member.absent or selected_member_status == ABSENT) and
              not self.household_member.eligible_member and not self.household_member.survival_status == DEAD):
            member_status = NOT_ELIGIBLE
        elif self.household_member.undecided or selected_member_status == UNDECIDED:
            member_status = UNDECIDED
        elif ((self.household_member.refused or selected_member_status == REFUSED) and
              not self.household_member.eligible_htc and
              not self.household_member.htc and not self.household_member.refused_htc):
            member_status = REFUSED
        return member_status

    def member_status(self, selected_member_status):
        """Returns the member_status based on the boolean values set in the signals, mostly."""
        member_status = self.update_member_status(selected_member_status)
        htc_status = not self.household_member.htc and not self.household_member.refused_htc
        if not member_status:
            if (self.household_member.refused and self.household_member.eligible_htc and htc_status):
                member_status = HTC_ELIGIBLE
            elif (not self.household_member.eligible_member and not self.household_member.eligible_htc and
                  not self.household_member.survival_status == DEAD):
                member_status = NOT_ELIGIBLE
            elif (not self.household_member.eligible_subject and
                  self.household_member.enrollment_checklist_completed and
                  not self.household_member.eligible_htc):
                member_status = NOT_ELIGIBLE
            elif self.household_member.htc:
                member_status = HTC
            elif self.household_member.refused_htc:
                member_status = REFUSED_HTC
            elif (not self.household_member.eligible_member and not self.household_member.eligible_subject and
                  self.household_member.eligible_htc):
                member_status = HTC_ELIGIBLE  # e.g over 64yrs or just not eligible for BHS
            elif (self.household_member.eligible_member and not self.household_member.eligible_subject and
                  self.household_member.eligible_htc):
                member_status = HTC_ELIGIBLE  # e.g failed enrollment
            elif self.household_member.eligible_member:
                member_status = ELIGIBLE_FOR_SCREENING  # new household_member instance
            else:
                pass
                # pprint.pprint(self.household_member.__dict__)
                # raise TypeError('cannot determine member_status. ')
        return member_status

    def update_options_eligible_member(self, options):
        if not self.household_member.eligible_subject:
            options.remove(ELIGIBLE_FOR_CONSENT)
            options.remove(BHS)
            if self.household_member.refused:
                options.remove(ABSENT)
                options.remove(UNDECIDED)
            if self.household_member.enrollment_loss_completed:
                options.remove(BHS_LOSS)
            if self.household_member.enrollment_checklist_completed:
                options.remove(ELIGIBLE_FOR_SCREENING)
        if not self.household_member.enrollment_checklist_completed:
            options.remove(BHS_LOSS)
        if not self.household_member.eligible_htc:
            options = [opt for opt in options if opt not in [HTC_ELIGIBLE, HTC]]
        elif self.household_member.eligible_htc:
            options = [ELIGIBLE_FOR_SCREENING]
        return options

    def update_options_not_eligible_member(self, options):
        if not self.household_member.eligible_htc:
            options = [NOT_ELIGIBLE]
        else:
            if self.household_member.htc:
                options = [HTC, ELIGIBLE_FOR_SCREENING]
            else:
                options = [HTC_ELIGIBLE, ELIGIBLE_FOR_SCREENING]
        return options

    def update_options_on_eligibity(self, options):
        if not self.household_member.eligible_member:
            options = self.update_options_not_eligible_member(options)
        elif self.household_member.eligible_member:
            options = [ABSENT, ELIGIBLE_FOR_SCREENING, ELIGIBLE_FOR_CONSENT, BHS, UNDECIDED, REFUSED, BHS_LOSS, HTC,
                       HTC_ELIGIBLE, DECEASED]
            if self.household_member.eligible_subject:
                options.remove(BHS_LOSS)
                options.remove(ELIGIBLE_FOR_SCREENING)
                options.remove(ABSENT)
                options.remove(UNDECIDED)
                if self.household_member.refused:
                    options.remove(BHS)
                    options.remove(ELIGIBLE_FOR_CONSENT)
                if not self.household_member.refused:
                    options.remove(HTC)
                    options.remove(HTC_ELIGIBLE)
            options = self.update_options_eligible_member(options)
        else:
            raise TypeError('ERROR: household_member.refused={0},self.household_member.eligible_htc={1}, '
                            'self.household_member.eligible_member={2} '
                            'should never occur together'.format(self.household_member.refused,
                                                                 self.household_member.eligible_htc,
                                                                 self.household_member.eligible_member))
        return options

    @property
    def member_status_choices(self):
        if not self.household_member.member_status:
            raise TypeError('household_member.member_status cannot be None')
        options = []
        if self.household_member.survival_status == DEAD:
            options = [ELIGIBLE_FOR_SCREENING]
        elif self.household_member.is_consented:
            if self.household_member.consented_in_previous_survey:
                options = [ANNUAL, ABSENT, REFUSED, UNDECIDED, HTC, DECEASED]
            else:
                options = [BHS]
        else:
            options = self.update_options_on_eligibity(options)
        # append the current member_status
        options.append(self.household_member.member_status)
        # sort and remove duplicates
        options = list(set(options))
        options.sort()
        return [(item, item) for item in options]
