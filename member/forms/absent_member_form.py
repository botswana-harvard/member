from ..models import AbsentMember, AbsentMemberEntry

from .base_membership_form import BaseMembershipForm


class AbsentMemberEntryForm(BaseMembershipForm):

    household_member_fk = 'absent_member'

    class Meta:
        model = AbsentMemberEntry
        fields = '__all__'


class AbsentMemberForm(BaseMembershipForm):

    class Meta:
        model = AbsentMember
        fields = '__all__'
