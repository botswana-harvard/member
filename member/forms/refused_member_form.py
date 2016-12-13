from ..models import RefusedMember

from .base_membership_form import BaseMembershipForm


class RefusedMemberForm(BaseMembershipForm):

    class Meta:
        model = RefusedMember
        fields = '__all__'
