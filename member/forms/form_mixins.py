import arrow

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import get_default_timezone

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_consent.site_consents import site_consents

from household.models import has_todays_log_entry_or_raise

from ..exceptions import EnumerationRepresentativeError


class MemberFormMixin(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(MemberFormMixin, self).clean()
        try:
            has_todays_log_entry_or_raise(
                cleaned_data.get('household_member').household_structure,
                report_datetime=cleaned_data.get('report_datetime'))
        except EnumerationRepresentativeError as e:
            raise forms.ValidationError(str(e))

        rdate = arrow.Arrow.fromdatetime(
            cleaned_data.get('report_datetime'), tzinfo=cleaned_data.get('report_datetime').tzinfo)
        try:
            obj = self._meta.model.objects.get(
                household_member=cleaned_data.get('household_member'),
                report_date=rdate.to('UTC').date())
        except ObjectDoesNotExist:
            pass
        else:
            if obj.id != self.instance.id:
                raise forms.ValidationError(
                    {'report_datetime': 'A report already exists for {}.'.format(
                        rdate.to(str(get_default_timezone())).date().strftime('%Y-%m-%d'))})

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
