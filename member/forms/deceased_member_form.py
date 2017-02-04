from django import forms

from edc_base.modelform_mixins import OtherSpecifyValidationMixin

from ..models import DeceasedMember


class DeceasedMemberForm (OtherSpecifyValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        self.validate_other_specify(
            'death_cause_info', 'death_cause_info_other')
        return cleaned_data

    class Meta:
        model = DeceasedMember
        fields = '__all__'
