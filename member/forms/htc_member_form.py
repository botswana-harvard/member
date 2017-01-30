from django import forms

from ..models import HtcMember

from edc_constants.constants import NOT_APPLICABLE, YES, NO


class HtcMemberForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('offered') == YES:
            self.offered_yes()
        else:
            self.offered_no()
        return cleaned_data

    def offered_yes(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('offered') == YES:
            if (cleaned_data.get('accepted') == YES
                    and cleaned_data.get('refusal_reason')):
                raise forms.ValidationError(
                    'You wrote HTC was accepted. A refusal reason is not applicable.')
            if (cleaned_data.get('accepted') == NO
                    and not cleaned_data.get('refusal_reason')):
                raise forms.ValidationError(
                    'You wrote HTC was not accepted. A refusal reason is required.')
            if cleaned_data.get('referred') == NOT_APPLICABLE:
                raise forms.ValidationError(
                    'Please indicate whether the subject was referred.')
            if (cleaned_data.get('referred') == YES
                    and not cleaned_data.get('referral_clinic')):
                raise forms.ValidationError(
                    'Please indicate the referral clinic.')
            if (cleaned_data.get('referred') == NO
                    and cleaned_data.get('referral_clinic')):
                raise forms.ValidationError(
                    'Subject was not referred. The referral clinic is not applicable.')

    def offered_no(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('accepted') != NOT_APPLICABLE:
            raise forms.ValidationError(
                'Household member was not offered HTC. Whether subject '
                'accepted is not applicable.')
        if cleaned_data.get('refusal_reason'):
            raise forms.ValidationError(
                'You wrote HTC was not offered. Refusal reason should be left blank.')
        if cleaned_data.get('referred') != NOT_APPLICABLE:
            raise forms.ValidationError(
                'Household member was not offered HTC. '
                'Whether subject was referred is not applicable.')
        if cleaned_data.get('referral_clinic'):
            raise forms.ValidationError(
                'Household member was not offered HTC. '
                'A referral clinic should be left blank.')

    class Meta:
        model = HtcMember
        fields = '__all__'
