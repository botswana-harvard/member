from django import forms

from member_form_validators.form_validators import HtcMemberFormValidator

from ..models import HtcMember


class HtcMemberForm (forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HtcMemberFormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        cleaned_data = form_validator.clean()
        return cleaned_data

    class Meta:
        model = HtcMember
        fields = '__all__'
