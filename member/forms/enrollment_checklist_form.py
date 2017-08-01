from django import forms
from django.conf import settings

from edc_base.exceptions import AgeValueError
from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_base.utils import age
from edc_constants.constants import NOT_APPLICABLE, NO, YES
from edc_registration.models import RegisteredSubject

from ..models import EnrollmentChecklist
from ..age_helper import AgeHelper


class EnrollmentChecklistForm(CommonCleanModelFormMixin, forms.ModelForm):

    age_helper_cls = AgeHelper

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('household_member'):
            raise forms.ValidationError(
                {'household_member': 'Field is required'})

        self.validate_may_modify()

        self.validate_citizen()

        non_citizen = (cleaned_data.get('citizen') == NO
                       and cleaned_data.get('legal_marriage') == NO)
        if non_citizen:
            if not settings.ANONYMOUS_ENABLED:
                raise forms.ValidationError(
                    'Non-citizens may not be enrolled at this time')
            if cleaned_data.get('dob'):
                raise forms.ValidationError({
                    'dob': 'This field is not required for non-citizens'})
            if cleaned_data.get('initials'):
                raise forms.ValidationError({
                    'initials': 'This field is not required for non-citizens'})
            if cleaned_data.get('has_identity'):
                raise forms.ValidationError({
                    'has_identity': 'This field is not required for non-citizens'})
        else:
            if not cleaned_data.get('dob'):
                raise forms.ValidationError({
                    'dob': 'This field is required'})
            if not cleaned_data.get('initials'):
                raise forms.ValidationError({
                    'initials': 'This field is required'})
            if not cleaned_data.get('has_identity'):
                raise forms.ValidationError({
                    'has_identity': 'This field is required'})
            self.validate_age()

        self.validate_study_participation()

        self.validate_with_registered_subject()
        return cleaned_data

    def validate_with_registered_subject(self):
        cleaned_data = self.cleaned_data
        household_member = cleaned_data.get('household_member')
        dob = cleaned_data.get('dob')
        initials = cleaned_data.get('initials')
        gender = cleaned_data.get('gender')
        non_citizen = (
            cleaned_data.get('citizen') == NO and
            cleaned_data.get('legal_marriage') == NO)
        try:
            registered_subject = RegisteredSubject.objects.get(
                subject_identifier=household_member.subject_identifier)
        except RegisteredSubject.DoesNotExist:
            pass
        else:
            if not non_citizen:
                if registered_subject.dob and registered_subject.dob != dob:
                    raise forms.ValidationError({
                        'dob': 'Incorrect date of birth. Based on a previous '
                        'registration expected {}.'.format(
                            registered_subject.dob)})
                elif registered_subject.initials and registered_subject.initials != initials:
                    raise forms.ValidationError({
                        'initials': 'Incorrect initials. Based on a previous '
                        'registration expected {}.'.format(
                            registered_subject.initials)})
                elif registered_subject.gender and registered_subject.gender != gender:
                    raise forms.ValidationError({
                        'initials': 'Incorrect gender. Based on a previous '
                        'registration expected {}.'.format(
                            registered_subject.gender)})

    def validate_may_modify(self):
        cleaned_data = self.cleaned_data
        household_member = cleaned_data.get('household_member')
        if household_member.is_consented:
            if (household_member.consent.survey_schedule_object.field_value
                    == household_member.survey_schedule_object.field_value):
                raise forms.ValidationError(
                    'Household member has consented. '
                    'Enrollment Checklist may not be modified')

    def validate_age(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('dob'):
            try:
                age_in_years = age(
                    cleaned_data.get('dob'),
                    cleaned_data.get('report_datetime')).years
            except AgeValueError as e:
                raise forms.ValidationError({'dob': str(e)})
            age_helper = self.age_helper_cls(
                age_in_years=age_in_years, **cleaned_data)
            age_helper.validate_or_raise()

    def validate_study_participation(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('study_participation') == NO:
            if not cleaned_data.get('confirm_participation') == NOT_APPLICABLE:
                raise forms.ValidationError({
                    'confirm_participation':
                    'This field is not required if never participated.'})

        if cleaned_data.get('study_participation') == YES:
            if cleaned_data.get('confirm_participation') == NOT_APPLICABLE:
                raise forms.ValidationError({
                    'confirm_participation':
                    'This field is required if previously participated.'})

    def validate_citizen(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('citizen') == NO:
            if cleaned_data.get('legal_marriage') == NOT_APPLICABLE:
                raise forms.ValidationError({
                    'legal_marriage':
                    'This field is applicable if not a citizen'})
            if (cleaned_data.get('legal_marriage') == YES and
                    cleaned_data.get('marriage_certificate') == NOT_APPLICABLE):
                raise forms.ValidationError({
                    'marriage_certificate':
                    'This field is applicable if legally marriage to a citizen.'})
            if (cleaned_data.get('legal_marriage') == NO
                    and cleaned_data.get('marriage_certificate') == YES):
                raise forms.ValidationError({
                    'marriage_certificate':
                    ('This field is not applicable if not legally married '
                     'to a citizen.')})
        elif cleaned_data.get('citizen') == YES:
            if cleaned_data.get('legal_marriage') != NOT_APPLICABLE:
                raise forms.ValidationError({
                    'legal_marriage':
                    'This field is not applicable if participant is a citizen.'})
            if cleaned_data.get('marriage_certificate') != NOT_APPLICABLE:
                raise forms.ValidationError({
                    'marriage_certificate':
                    'This field is not applicable if participant is a citizen.'})

    class Meta:
        model = EnrollmentChecklist
        fields = '__all__'
