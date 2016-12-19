from ..models import UndecidedMember

from .form_mixins import MemberFormMixin


class UndecidedMemberForm(MemberFormMixin):

    class Meta:
        model = UndecidedMember
        fields = '__all__'
