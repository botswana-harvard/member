from django import forms

from ..form_validators import HouseholdInfoFormValidator
from ..models import HouseholdInfo


class HouseholdInfoForm (forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HouseholdInfoFormValidator(cleaned_data=cleaned_data)
        cleaned_data = form_validator.clean()
        return cleaned_data

    class Meta:
        model = HouseholdInfo
        fields = '__all__'
