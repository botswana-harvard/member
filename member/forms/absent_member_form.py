from ..models import AbsentMember
from .form_mixins import MemberFormMixin


class AbsentMemberForm(MemberFormMixin):

    class Meta:
        model = AbsentMember
        fields = '__all__'
