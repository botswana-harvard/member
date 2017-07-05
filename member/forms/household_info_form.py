from django import forms

from member_form_validators.form_validators import HouseholdInfoFormValidator

from ..models import HouseholdInfo


class HouseholdInfoForm (forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HouseholdInfoFormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        cleaned_data = form_validator.clean()
        return cleaned_data

    class Meta:
        model = HouseholdInfo
        fields = '__all__'
