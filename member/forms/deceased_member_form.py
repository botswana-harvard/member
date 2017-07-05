from django import forms

from member_form_validators.form_validators import DeceasedMemberFormValidator

from ..models import DeceasedMember


class DeceasedMemberForm (forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = DeceasedMemberFormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        return form_validator.clean()

    class Meta:
        model = DeceasedMember
        fields = '__all__'
