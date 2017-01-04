from django import forms

from edc_base.exceptions import AgeValueError
from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_base.utils import age
from edc_constants.constants import NOT_APPLICABLE, NO, YES

from ..models import EnrollmentChecklist


class EnrollmentChecklistForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(EnrollmentChecklistForm, self).clean()
        if not cleaned_data.get('household_member'):
            raise forms.ValidationError({'household_member': 'Field is required'})
        if cleaned_data.get('household_member').is_consented:
            raise forms.ValidationError(
                'Household member has consented. Enrollment Checklist may not be modified')
        self.validate_study_participation()
        self.validate_citizen()
        self.validate_age()
        return cleaned_data

    def validate_age(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('dob'):
            try:
                age_in_years = age(cleaned_data.get('dob'), cleaned_data.get('report_datetime')).years
            except AgeValueError as e:
                raise forms.ValidationError({'dob': str(e)})
            if age_in_years in [16, 17] and cleaned_data.get('is_minor') == NOT_APPLICABLE:
                raise forms.ValidationError(
                    'Subject a minor. Got {0} years. Answer to \'if minor, is there '
                    'guardian available\', cannot be N/A.'.format(age_in_years))
            if age_in_years > 17 and not cleaned_data.get('guardian') == NOT_APPLICABLE:
                raise forms.ValidationError(
                    'Subject a not minor. Got {0} years. Answer to \'if minor, is '
                    'there guardian available\', should be N/A.'.format(age_in_years))

    def validate_study_participation(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('study_participation') == NO:
            if not cleaned_data.get('confirm_participation') == NOT_APPLICABLE:
                raise forms.ValidationError({
                    'confirm_participation': 'This field is not required if never participated.'})

        if cleaned_data.get('study_participation') == YES:
            if cleaned_data.get('confirm_participation') == NOT_APPLICABLE:
                raise forms.ValidationError({
                    'confirm_participation': 'This field is required if previously participated.'})

    def validate_citizen(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('citizen') == NO:
            if cleaned_data.get('legal_marriage') == NOT_APPLICABLE:
                raise forms.ValidationError({
                    'legal_marriage': 'This field is applicable if not a citizen'})
            if (cleaned_data.get('legal_marriage') == YES and
                    cleaned_data.get('marriage_certificate') == NOT_APPLICABLE):
                raise forms.ValidationError({
                    'marriage_certificate': 'This field is applicable if legally marriage to a citizen.'})
            if cleaned_data.get('legal_marriage') == NO and cleaned_data.get('marriage_certificate') == YES:
                raise forms.ValidationError({
                    'marriage_certificate': (
                        'This field is not applicable if not legally married to a citizen.')})
        elif cleaned_data.get('citizen') == YES:
            if cleaned_data.get('legal_marriage') != NOT_APPLICABLE:
                raise forms.ValidationError({
                    'legal_marriage': 'This field is not applicable if participant is a citizen.'})
            if cleaned_data.get('marriage_certificate') != NOT_APPLICABLE:
                raise forms.ValidationError({
                    'marriage_certificate': 'This field is not applicable if participant is a citizen.'})

    class Meta:
        model = EnrollmentChecklist
        fields = '__all__'
