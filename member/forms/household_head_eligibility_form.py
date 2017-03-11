from django import forms

from ..models import HouseholdHeadEligibility


class HouseholdHeadEligibilityForm(forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('household_member'):
            raise forms.ValidationError({'household_member': 'Required.'})
        household_member = cleaned_data.get('household_member')
        if not household_member.age_in_years >= 18:
            raise forms.ValidationError(
                'Member must be over 18 years of age. Got {0}.'.format(
                    household_member.age_in_years))
        return super(HouseholdHeadEligibilityForm, self).clean()

    class Meta:
        model = HouseholdHeadEligibility
        fields = '__all__'
