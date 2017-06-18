from django import forms

from ..form_validators import HouseholdMemberFormValidator
from ..models import HouseholdMember


class HouseholdMemberForm (forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HouseholdMemberFormValidator(
            cleaned_data=cleaned_data)
        cleaned_data = form_validator.clean()
        return cleaned_data

    class Meta:
        model = HouseholdMember
        fields = '__all__'
