from django import forms
from datetime import date
from dateutil.relativedelta import relativedelta

from edc_constants.constants import NOT_APPLICABLE

from ..models import EnrollmentChecklist
from ..exceptions import MemberEnrollmentError


class EnrollmentChecklistForm(forms.ModelForm):

    def validate_study_participation(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('study_participation') == 'No':
            if not cleaned_data.get('confirm_participation') == NOT_APPLICABLE:
                raise forms.ValidationError('Confirmation on study participation is not required.'
                                            'The question is not applicable')

        if cleaned_data.get('study_participation') == 'Yes':
            if cleaned_data.get('confirm_participation') == NOT_APPLICABLE:
                raise forms.ValidationError('Confirmation on study participation required.'
                                            'The answer can not be Not Applicable.')

    def validate_citizen(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('citizen') == 'No':
            if cleaned_data.get('legal_marriage') == NOT_APPLICABLE:
                raise forms.ValidationError('Participant is not a citizen, indicate if he/she is legally '
                                            'married to a Botswana citizen.')
            if (cleaned_data.get('legal_marriage') == 'Yes' and
                    cleaned_data.get('marriage_certificate') == NOT_APPLICABLE):
                raise forms.ValidationError('Participant is a non-citizen married to a citizen, indicate '
                                            'if he/she produced marriage certificate as proof.')
            if cleaned_data.get('legal_marriage') == 'No' and cleaned_data.get('marriage_certificate') == 'Yes':
                raise forms.ValidationError('Participant is a non-citizen NOT married to a citizen, '
                                            'there cannot be a marriage certificate.')

    def clean(self):
        cleaned_data = super(EnrollmentChecklistForm, self).clean()
        if not cleaned_data.get('household_member'):
            raise forms.ValidationError('Please select a household member.')

        if cleaned_data.get('household_member').is_consented:
            raise forms.ValidationError('Household member has consented. Enrollment Checklist may not be modified')

        self.instance.matches_household_member_values(EnrollmentChecklist(**cleaned_data),
                                                      cleaned_data.get('household_member'),
                                                      forms.ValidationError)

        if cleaned_data.get('citizen') == 'Yes':
            if not cleaned_data.get('legal_marriage') == NOT_APPLICABLE:
                raise forms.ValidationError('Marital status is not applicable, Participant is a citizen.')
            if not cleaned_data.get('marriage_certificate') == NOT_APPLICABLE:
                raise forms.ValidationError('Marriage Certificate is not applicable, Participant is a citizen.')

        self.study_participation()
        self.validate_citizen()

        age_in_years = relativedelta(date.today(), cleaned_data.get('dob')).years
        if age_in_years in [16, 17] and cleaned_data.get('is_minor') == NOT_APPLICABLE:
            raise forms.ValidationError('Subject a minor. Got {0} years. Answer to \'if minor, is there '
                                        'guardian available\', cannot be N/A.'.format(age_in_years))
        if age_in_years > 17 and not cleaned_data.get('guardian') == NOT_APPLICABLE:
            raise forms.ValidationError('Subject a not minor. Got {0} years. Answer to \'if minor, is '
                                        'there guardian available\', should be N/A.'.format(age_in_years))

        try:
            instance = self._meta.model(id=self.instance.id, **cleaned_data)
            instance.common_clean()
        except MemberEnrollmentError as e:
            raise forms.ValidationError(str(e))
        return cleaned_data

    class Meta:
        model = EnrollmentChecklist
        fields = '__all__'
