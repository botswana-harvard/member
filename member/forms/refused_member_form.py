from ..models import RefusedMember

from .form_mixins import MemberFormMixin


class RefusedMemberForm(MemberFormMixin):

    class Meta:
        model = RefusedMember
        fields = '__all__'
