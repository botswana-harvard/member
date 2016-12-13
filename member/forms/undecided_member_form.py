from ..models import UndecidedMember, UndecidedMemberEntry

from .form_mixins import MemberFormMixin


class UndecidedMemberEntryForm(MemberFormMixin):

    household_member_fk = 'undecided_member'

    class Meta:
        model = UndecidedMemberEntry
        fields = '__all__'


class UndecidedMemberForm(MemberFormMixin):

    class Meta:
        model = UndecidedMember
        fields = '__all__'
