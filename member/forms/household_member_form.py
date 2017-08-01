from django import forms

from edc_base.modelform_validators import FormValidatorMixin
from member_form_validators.form_validators import HouseholdMemberFormValidator

from ..models import HouseholdMember


class HouseholdMemberForm (FormValidatorMixin, forms.ModelForm):

    form_validator_cls = HouseholdMemberFormValidator

    #     details_change_reason = forms.ChoiceField(
    #         label='If YES, please specify the reason',
    #         widget=forms.TextInput(attrs={'size': 30}),
    #         required=False,
    #         choices=DETAILS_CHANGE_REASON,
    #         help_text=('if personal detail changed indicate the reason.'))

    class Meta:
        model = HouseholdMember
        fields = '__all__'
