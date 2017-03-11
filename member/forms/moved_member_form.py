from django import forms

from edc_constants.constants import YES, NO

from ..models import MovedMember

from .form_mixins import MemberFormMixin


class MovedMemberForm(MemberFormMixin):

    def clean(self):
        cleaned_data = self.cleaned_data

        if (cleaned_data.get('moved_household') == NO
                and cleaned_data.get('moved_community') == YES):
            raise forms.ValidationError(
                'You have indicated that the participant has NOT '
                'moved out of the household but HAS '
                'moved out of the community. Please correct.')

        if (cleaned_data.get('moved_community') == YES
                and not cleaned_data.get('new_community')):
            raise forms.ValidationError(
                'Specify the name of the new community or UNKNOWN. '
                'Got participant has moved out of the community.')

        if (cleaned_data.get('moved_community') != YES
                and cleaned_data.get('new_community')):
            raise forms.ValidationError(
                'Participant has NOT moved out of the community. '
                'Do not specify a new community.')

        return self.cleaned_data

    class Meta:
        model = MovedMember
        fields = '__all__'
