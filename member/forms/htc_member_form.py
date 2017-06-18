from django import forms

from ..form_validators import HtcMemberFormValidator
from ..models import HtcMember


class HtcMemberForm (forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HtcMemberFormValidator(
            cleaned_data=cleaned_data)
        cleaned_data = form_validator.clean()
        return cleaned_data

    class Meta:
        model = HtcMember
        fields = '__all__'
