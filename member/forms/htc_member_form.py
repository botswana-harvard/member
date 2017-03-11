from django import forms

from edc_base.modelform_mixins import RequiredFieldValidationMixin, ApplicableValidationMixin
from edc_constants.constants import YES, NO

from ..models import HtcMember


class HtcMemberForm(RequiredFieldValidationMixin, ApplicableValidationMixin,
                    forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        self.required_if(
            NO, field='accepted', field_required='refusal_reason')
        self.applicable_if(YES, field='offered', field_applicable='referred')
        self.required_if(
            YES, field='referred', field_required='referral_clinic')
        return cleaned_data

    class Meta:
        model = HtcMember
        fields = '__all__'
