from django import forms
from django.apps import apps as django_apps


class BaseMembershipForm(forms.ModelForm):

    def clean(self):
        SubjectConsent = django_apps.get_model('bcpp_subject', 'SubjectConsent')
        cleaned_data = super(BaseMembershipForm, self).clean()
        if cleaned_data:
            household_member = cleaned_data.get('household_member', None)
            if not household_member:
                household_member = cleaned_data.get(self.household_member_fk, None).household_member
            if not household_member:
                raise forms.ValidationError('Unable to determine the household structure member for this instance.')
            subject_consent = SubjectConsent.objects.filter(household_member=household_member)
            if subject_consent:
                subject_consent = SubjectConsent.objects.get(household_member=household_member)
                if cleaned_data.get('report_datetime', None) > subject_consent.consent_datetime:
                    raise forms.ValidationError('Report may not be submitted for survey {}. '
                                                'Subject is already consented for this survey.'.format(
                                                    subject_consent.survey.survey_name,))
        return cleaned_data
