from django import forms

from ..models import HouseholdHeadEligibility


class HouseholdHeadEligibilityForm(forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('household_member', None) is None:
            raise forms.ValidationError('You have to select a household member in order to save.')
        self.instance.matches_household_member_values(cleaned_data.get('household_member'), forms.ValidationError)
        return super(HouseholdHeadEligibilityForm, self).clean()

    class Meta:
        model = HouseholdHeadEligibility
        fields = '__all__'
