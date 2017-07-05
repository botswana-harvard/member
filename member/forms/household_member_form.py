from django import forms

from member_form_validators.form_validators import HouseholdMemberFormValidator

from ..models import HouseholdMember


class HouseholdMemberForm (forms.ModelForm):

    #     details_change_reason = forms.ChoiceField(
    #         label='If YES, please specify the reason',
    #         widget=forms.TextInput(attrs={'size': 30}),
    #         required=False,
    #         choices=DETAILS_CHANGE_REASON,
    #         help_text=('if personal detail changed indicate the reason.'))

    def clean(self):
        cleaned_data = super().clean()
        form_validator = HouseholdMemberFormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        form_validator.validate()
        return cleaned_data

    class Meta:
        model = HouseholdMember
        fields = '__all__'
