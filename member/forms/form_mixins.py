from django import forms
from django.apps import apps as django_apps
from edc_base.modelform_mixins import CommonCleanModelFormMixin


class MemberFormMixin(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(MemberFormMixin, self).clean()
        if cleaned_data:
            SubjectConsent = django_apps.get_model(*'subject.subjectconsent'.split('.'))
            household_member = cleaned_data.get('household_member')
            try:
                subject_consent = SubjectConsent.objects.get(household_member=household_member)
                if cleaned_data.get('report_datetime') > subject_consent.consent_datetime:
                    raise forms.ValidationError('Report may not be submitted for survey {}. '
                                                'Subject is already consented for this survey.'.format(
                                                    subject_consent.survey.survey_name,))
            except SubjectConsent.DoesNotExist:
                pass
        return cleaned_data
