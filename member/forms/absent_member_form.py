from ..models import AbsentMember, AbsentMemberEntry

from .form_mixins import MemberFormMixin


class AbsentMemberEntryForm(MemberFormMixin):

    household_member_fk = 'absent_member'

    class Meta:
        model = AbsentMemberEntry
        fields = '__all__'


class AbsentMemberForm(MemberFormMixin):

    class Meta:
        model = AbsentMember
        fields = '__all__'
