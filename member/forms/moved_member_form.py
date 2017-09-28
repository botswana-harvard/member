from member_form_validators.form_validators import MovedMemberFormValidator

from ..models import MovedMember
from .form_mixins import MemberFormMixin


class MovedMemberForm(MemberFormMixin):

    form_validator_cls = MovedMemberFormValidator

    class Meta:
        model = MovedMember
        fields = '__all__'
