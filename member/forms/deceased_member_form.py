from django import forms

from edc_base.modelform_validators import FormValidatorMixin
from member_form_validators import DeceasedMemberFormValidator

from ..models import DeceasedMember


class DeceasedMemberForm (FormValidatorMixin, forms.ModelForm):

    form_validator_cls = DeceasedMemberFormValidator

    class Meta:
        model = DeceasedMember
        fields = '__all__'
