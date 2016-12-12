from django import forms

from ..models import MemberAppointment


class MemberAppointmentForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(MemberAppointmentForm, self).clean()
        return cleaned_data

    class Meta:
        model = MemberAppointment
        fields = '__all__'
