import arrow

from django import forms
from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_consent.site_consents import site_consents
from django.utils.timezone import get_default_timezone
from member.models.household_member.utils import has_todays_log_entry_or_raise
from member.exceptions import EnumerationRepresentativeError


class MemberFormMixin(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(MemberFormMixin, self).clean()
        try:
            has_todays_log_entry_or_raise(cleaned_data.get('household_member').household_structure)
        except EnumerationRepresentativeError as e:
            raise forms.ValidationError(str(e))
        report_dt = arrow.Arrow.fromdate(
            cleaned_data.get('report_date'), tzinfo=get_default_timezone()).datetime
        consent = site_consents.get_consent(
            report_datetime=report_dt)
        household_member = cleaned_data.get('household_member')
        try:
            subject_consent = consent.model.objects.get(
                household_member=household_member,
                version=consent.version)
            if report_dt > subject_consent.consent_datetime:
                raise forms.ValidationError(
                    'Report may not be submitted for survey {}. '
                    'Subject is already consented for this survey.'.format(
                        subject_consent.survey.survey_name,))
        except consent.model.DoesNotExist:
            pass
        return cleaned_data
