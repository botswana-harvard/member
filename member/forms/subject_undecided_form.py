from ..models import UndecidedMember, UndecidedMemberEntry

from .base_membership_form import BaseMembershipForm


class UndecidedMemberEntryForm(BaseMembershipForm):

    household_member_fk = 'undecided_member'

    class Meta:
        model = UndecidedMemberEntry
        fields = '__all__'


class UndecidedMemberForm(BaseMembershipForm):

    class Meta:
        model = UndecidedMember
        fields = '__all__'
