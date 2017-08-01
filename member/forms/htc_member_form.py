from django import forms

from edc_base.modelform_validators import FormValidatorMixin
from member_form_validators.form_validators import HtcMemberFormValidator

from ..models import HtcMember


class HtcMemberForm (FormValidatorMixin, forms.ModelForm):

    form_validator_cls = HtcMemberFormValidator

    class Meta:
        model = HtcMember
        fields = '__all__'
