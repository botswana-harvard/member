import arrow

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import get_default_timezone

from edc_base.modelform_mixins import CommonCleanModelFormMixin

from household.exceptions import HouseholdLogRequired
from household.models import todays_log_entry_or_raise


class MemberFormMixin(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(MemberFormMixin, self).clean()
        try:
            todays_log_entry_or_raise(
                household_structure=cleaned_data.get(
                    'household_member').household_structure,
                report_datetime=cleaned_data.get('report_datetime'))
        except HouseholdLogRequired as e:
            raise forms.ValidationError(str(e))

        rdate = arrow.Arrow.fromdatetime(
            cleaned_data.get('report_datetime'),
            tzinfo=cleaned_data.get('report_datetime').tzinfo)
        try:
            obj = self._meta.model.objects.get(
                household_member=cleaned_data.get('household_member'),
                report_datetime__date=rdate.to('UTC').date())
        except ObjectDoesNotExist:
            pass
        else:
            if obj.id != self.instance.id:
                raise forms.ValidationError(
                    {'report_datetime':
                     'A report already exists for {}.'.format(
                         rdate.to(str(get_default_timezone())).date().strftime(
                             '%Y-%m-%d'))})

        household_member = cleaned_data.get('household_member')
        if household_member.consent:
            if (cleaned_data.get('report_datetime')
                    > household_member.consent.consent_datetime):
                raise forms.ValidationError(
                    'Report may not be submitted for survey \'{}\'. '
                    'Subject is already consented for this survey.'.format(
                        household_member.consent.survey_schedule_object.name))
        return cleaned_data
