from django import forms

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_consent.site_consents import site_consents

from ..models.household_member import has_todays_log_entry_or_raise
from member.exceptions import EnumerationRepresentativeError


class MemberFormMixin(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(MemberFormMixin, self).clean()
        try:
            has_todays_log_entry_or_raise(
                cleaned_data.get('household_member').household_structure,
                report_datetime=cleaned_data.get('report_datetime'))
        except EnumerationRepresentativeError as e:
            raise forms.ValidationError(str(e))
        consent = site_consents.get_consent(
            report_datetime=cleaned_data.get('report_datetime'))
        household_member = cleaned_data.get('household_member')
        try:
            subject_consent = consent.model.objects.get(
                household_member=household_member,
                version=consent.version)
            if cleaned_data.get('report_datetime') > subject_consent.consent_datetime:
                raise forms.ValidationError(
                    'Report may not be submitted for survey {}. '
                    'Subject is already consented for this survey.'.format(
                        subject_consent.survey.survey_name,))
        except consent.model.DoesNotExist:
            pass
        return cleaned_data
