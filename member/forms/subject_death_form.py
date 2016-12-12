from django import forms

from ..models import SubjectDeath


class SubjectDeathForm (forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'other' in cleaned_data['death_cause_info'].name.lower() and not cleaned_data['death_cause_info_other']:
            raise forms.ValidationError(
                'You wrote \'other\' for the source of information for the cause of death category. Please specify.')
        if 'other' in cleaned_data['death_cause_category'].name.lower() and not cleaned_data['death_cause_other']:
            raise forms.ValidationError('You wrote \'other\' for the cause of death category. Please specify.')
        return cleaned_data

    class Meta:
        model = SubjectDeath
        fields = '__all__'
