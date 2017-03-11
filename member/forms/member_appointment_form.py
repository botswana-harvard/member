from django import forms

from ..models import MemberAppointment


class MemberAppointmentForm(forms.ModelForm):

    class Meta:
        model = MemberAppointment
        fields = '__all__'
