from django import forms
from edc_base.modelform_validators import FormValidatorMixin
from member_form_validators.form_validators import HouseholdInfoFormValidator

from ..models import HouseholdInfo


class HouseholdInfoForm (FormValidatorMixin, forms.ModelForm):

    form_validator_cls = HouseholdInfoFormValidator

    class Meta:
        model = HouseholdInfo
        fields = '__all__'
