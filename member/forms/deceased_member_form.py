from django import forms

from member_form_validators import DeceasedMemberFormValidator

from ..models import DeceasedMember


class DeceasedMemberForm (forms.ModelForm):

    form_validator_cls = DeceasedMemberFormValidator

    class Meta:
        model = DeceasedMember
        fields = '__all__'
